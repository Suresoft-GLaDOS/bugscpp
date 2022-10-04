"""
Core module of defining commands.

Inherit from the classes to add a new command:
- SimpleCommand
- ShellCommand
- DockerCommand

Note that the module name of a newly defined command will be the command name.
For instance, if MyNewCommand is defined at my_command.py,
MyNewCommand can be invoked from "d++ my_command" at command-line.
"""
import argparse
import stat
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Generator, List, Optional, Tuple

import taxonomy
from config import config
from errors import DppCommandListInternalError
from message import message
from processor.core.data import Worktree
from processor.core.docker import Docker
from processor.core.shell import Shell


class CommandRegistryMeta(type):
    """
    Metaclass which auto registers class.

    The module name will be command to invoke associated class.
    All registered commands can be retrieved via 'RegisteredCommands'.

    Methods
    -------
    get_commands : Dict[str, Command]
        Returns a dictionary of registered commands.

    See Also
    --------
    RegisteredCommands : Get a list of registered commands.
    """

    _commands: Dict[str, "Command"] = {}

    def __new__(mcs, name, bases, attrs):
        new_class = type.__new__(mcs, name, bases, attrs)
        m = attrs["__module__"]
        if m != __name__ and not getattr(new_class, "_ignore_registry", False):
            CommandRegistryMeta._commands[m.split(".")[-1]] = new_class()
        return new_class

    @staticmethod
    def get_commands() -> Dict[str, "Command"]:
        return CommandRegistryMeta._commands


class AbstractCommandRegistryMeta(CommandRegistryMeta, ABCMeta):
    """
    Class that combines CommandRegistryMeta with ABCMeta.
    """

    pass


class BaseCommandRegistry(ABC, metaclass=AbstractCommandRegistryMeta):
    """
    Base class of CommandRegistry.
    """

    pass


class Command(BaseCommandRegistry):
    """
    Abstract class to implement a command.
    Inherit from this class to add a new command.
    The name of the command will be identical to the module name where the class is defined.
    If there are multiple classes inherited from this inside the module,
    the last one will be applied.
    """

    @property
    def group(self) -> str:
        """Represent the group of this command. It is not meaningful yet."""
        raise NotImplementedError

    @property
    def help(self) -> str:
        """Description of this command."""
        raise NotImplementedError

    @abstractmethod
    def __call__(self, argv: List[str]):
        """The actual behavior of the command."""
        raise NotImplementedError


class RegisteredCommands:
    """
    Descriptor to access registered commands.
    Pass a module name to retrieve an instance of associated class.
    """

    def __get__(self, instance, owner) -> Dict[str, Command]:
        return CommandRegistryMeta.get_commands()

    def __set__(self, instance, value):
        raise DppCommandListInternalError()


class SimpleCommand(Command):
    """
    Command that does not use docker.
    Not fully implemented yet.
    """

    @property
    def group(self) -> str:
        return "v1"

    @abstractmethod
    def run(self, argv: List[str]) -> bool:
        raise NotImplementedError

    def __call__(self, argv: List[str]) -> bool:
        return self.run(argv)


@dataclass
class ShellCommandArguments:
    commands: List[str]


class ShellCommand(Command):
    """
    Command that does not use docker but shell instead.
    Not fully implemented yet.
    """

    def __init__(self):
        pass

    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        shell_args = self.run(argv)
        with Shell() as shell:
            shell.send(shell_args.commands)

    @abstractmethod
    def run(self, argv: List[str]) -> ShellCommandArguments:
        raise NotImplementedError


class DockerCommandScript(metaclass=ABCMeta):
    """
    A list of "DockerCommand"s to be serially executed
    """

    def __init__(self, command_type: taxonomy.CommandType, command: List[str]):
        self.type = command_type
        self.lines: Tuple[str] = tuple(command)

    @abstractmethod
    def before(self):
        """
        Invoked before script is executed.
        """
        raise NotImplementedError

    @abstractmethod
    def step(self, linenr: int, line: str):
        """
        Invoked before each line is executed.

        Parameters
        ----------
        linenr : int
            The current line number.
        line: str
            The current line to execute.
        """
        pass

    @abstractmethod
    def output(self, linenr: Optional[int], exit_code: Optional[int], output: str):
        """
        Invoked after each line is executed.
        linenr is None if all commands are executed as if it is a script.

        Parameters
        ----------
        linenr : Optional[int]
            Index of the commands which has been executed.
            None if the type is CommandType.Script.
        exit_code: Optional[int]
            Exit code of the executed command.
            None when stream is set to False.
        output : str
            Captured stdout of the executed command.
        """
        pass

    @abstractmethod
    def after(self):
        """
        Invoked after script is executed.
        """
        raise NotImplementedError

    def __iter__(self):
        return iter(self.lines)

    def should_be_run_at_once(self) -> bool:
        """
        Returns
        -------
        bool
            Return true if it should be written to a file and executed at once,
            otherwise if it is sent to a container line by line.
        """
        return self.type == taxonomy.CommandType.Script


class DockerCommandScriptGenerator(metaclass=ABCMeta):
    """
    Factory class of DockerCommandScript.
    """

    def __init__(self, metadata: taxonomy.MetaData, worktree: Worktree, stream: bool):
        self._metadata = metadata
        self._worktree = worktree
        self._stream = stream

    @property
    def metadata(self):
        """
        Metadata information of the current script.
        """
        return self._metadata

    @property
    def worktree(self):
        """Worktree information of the current script."""
        return self._worktree

    @property
    def stream(self):
        """True if command should be streamed, otherwise False."""
        return self._stream

    @abstractmethod
    def create(self) -> Generator[DockerCommandScript, None, None]:
        """Yield DockerCommandScript."""
        raise NotImplementedError


class DockerCommand(Command):
    """
    Executes each command of DockerCommandLine one by one inside a docker container.
    Inherit from this class to implement a new command that should be run inside a docker.

    Methods
    -------
    __call__ : None
        Execute commands.
    """

    SCRIPT_NAME = "DPP_COMMAND_SCRIPT"

    def __init__(self, parser: argparse.ArgumentParser):
        self.parser = parser
        self.environ: Dict[str, str] = {}

    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        """
        Execute commands inside a container.

        Parameters
        ----------
        argv : List[str]
            Command line argument vector.

        Returns
        -------
        None
        """

        def parse_exec_result(ec, output, line_number: Optional[int] = None) -> None:
            # Depending on 'stream' value, return value is a bit different.
            # 'exit_code' is None when 'stream' is True.
            # https://docker-py.readthedocs.io/en/stable/containers.html
            if ec is None:
                for stream_line in output:
                    message.stdout_stream(stream_line.decode("utf-8", errors="ignore"))
            else:
                script.output(line_number, ec, output.decode("utf-8", errors="ignore"))

        args = self.parser.parse_args(argv)

        if args.jobs <= 0:
            raise ValueError("jobs must be greater than 0")
        else:
            config.DPP_PARALLEL_BUILD = str(args.jobs)

        self.environ = args.env

        script_generator = self.create_script_generator(args)
        worktree = script_generator.worktree
        stream = script_generator.stream
        rebuild_image = True if args.rebuild_image else False
        user = ""  # root
        uid = args.uid if hasattr(args, "uid") and args.uid is not None else None

        self.setup(script_generator)
        with Docker(
            script_generator.metadata.dockerfile,
            script_generator.worktree,
            self.environ,
            rebuild_image,
            user,
            uid,
        ) as docker:
            for script in script_generator.create():
                script.before()
                if script.should_be_run_at_once():
                    file = Path(f"{worktree.host}/{DockerCommand.SCRIPT_NAME}")
                    with open(file, "w+") as fp:
                        fp.write("\n".join(script))
                    file.chmod(
                        file.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
                    )
                    exit_code, output_stream = docker.send(
                        f"{worktree.container}/{DockerCommand.SCRIPT_NAME}", stream
                    )
                    parse_exec_result(exit_code, output_stream)
                else:
                    for linenr, line in enumerate(script, start=1):
                        script.step(linenr, line)
                        exit_code, output_stream = docker.send(line, stream)
                        parse_exec_result(exit_code, output_stream, linenr)
                script.after()
        self.teardown(script_generator)

    @abstractmethod
    def create_script_generator(
        self, args: argparse.Namespace
    ) -> DockerCommandScriptGenerator:
        """
        Return DockerExecInfo which has information of a command list to run inside docker container.

        Parameters
        ----------
        args : argparse.Namespace
            argparse.Namespace instance.

        Returns
        -------
        DockerCommandScriptGenerator
            An instance of generator class which is used to create DockerCommandScript.
        """
        raise NotImplementedError

    @abstractmethod
    def setup(self, generator: DockerCommandScriptGenerator):
        """
        Invoked before container is created.

        Parameters
        ----------
        generator : DockerCommandScriptGenerator
            The current instance being used.
        """
        raise NotImplementedError

    @abstractmethod
    def teardown(self, generator: DockerCommandScriptGenerator):
        """
        Invoked after container is destroyed.

        Parameters
        ----------
        generator : DockerCommandScriptGenerator
            The current instance being used.
        """
        raise NotImplementedError
