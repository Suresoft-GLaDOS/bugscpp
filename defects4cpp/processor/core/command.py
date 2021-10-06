import stat
from abc import ABC, ABCMeta, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, List, Optional, Dict

import message
import taxonomy
from errors import DppCommandListInternalError
from processor.core.docker import Docker, Worktree
from processor.core.shell import Shell


class CommandRegistryMeta(type):
    _commands: Dict[str, "Command"] = {}

    def __new__(mcs, name, bases, attrs):
        new_class = type.__new__(mcs, name, bases, attrs)
        m = attrs["__module__"]
        if m != __name__:
            CommandRegistryMeta._commands[m.split(".")[-1]] = new_class()
        return new_class

    @staticmethod
    def get_commands() -> Dict[str, "Command"]:
        return CommandRegistryMeta._commands


class AbstractCommandRegistryMeta(CommandRegistryMeta, ABCMeta):
    pass


class BaseCommandRegistry(ABC, metaclass=AbstractCommandRegistryMeta):
    pass


class Command(BaseCommandRegistry):
    @property
    def group(self) -> str:
        raise NotImplementedError

    @property
    def help(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, argv: List[str]):
        raise NotImplementedError


class RegisteredCommands:
    def __get__(self, instance, owner) -> Dict[str, Command]:
        return CommandRegistryMeta.get_commands()

    def __set__(self, instance, value):
        raise DppCommandListInternalError()


class SimpleCommand(Command):
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
    A bulk of commands which is executed one by one by DockerCommand.
    """

    def __init__(self, command_type: taxonomy.CommandType, command: List[str]):
        self.type = command_type
        self.lines = command

    @abstractmethod
    def before(self):
        """
        Invoked before script is executed.
        """
        raise NotImplementedError

    @abstractmethod
    def output(self, linenr: Optional[int], exit_code: Optional[int], output: str):
        """
        Invoked after each line is executed only if docker is executed with stream set to False.
        linenr is None if all commands are executed as if it is a script.
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

    def should_be_run_at_once(self):
        """
        Returns true if it should be written to a file and executed at once,
        otherwise if it is sent to a container line by line.
        """
        return self.type == taxonomy.CommandType.Script


class DockerCommandScriptGenerator(metaclass=ABCMeta):
    """
    Factory class of DockerCommandScript
    """

    def __init__(self, metadata: taxonomy.MetaData, worktree: Worktree, stream: bool):
        # TODO: property?
        self.metadata = metadata
        self.worktree = worktree
        self.stream = stream

    @abstractmethod
    def create(self) -> Generator[DockerCommandScript, None, None]:
        raise NotImplementedError


class DockerCommand(Command):
    """
    Executes each command of DockerCommandLine one by one inside docker container.
    """

    SCRIPT_NAME = "DPP_COMMAND_SCRIPT"

    def __init__(self):
        pass

    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        def parse_exec_result(ec, output, line_number: Optional[int] = None) -> None:
            # Depending on 'stream' value, return value is a bit different.
            # 'exit_code' is None when 'stream' is True.
            # https://docker-py.readthedocs.io/en/stable/containers.html
            if ec is None:
                for stream_line in output:
                    message.docker(stream_line.decode("utf-8", errors="ignore"))
            else:
                script.output(line_number, ec, output.decode("utf-8", errors="ignore"))

        script_generator = self.create_script_generator(argv)
        worktree = script_generator.worktree
        stream = script_generator.stream

        self.setup(script_generator)
        with Docker(
            script_generator.metadata.dockerfile, script_generator.worktree
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
                        exit_code, output_stream = docker.send(line, stream)
                        parse_exec_result(exit_code, output_stream, linenr)
                script.after()
        self.teardown(script_generator)

    @abstractmethod
    def create_script_generator(self, argv: List[str]) -> DockerCommandScriptGenerator:
        """
        Return DockerExecInfo which has information of a command list to run inside docker container.
        """
        raise NotImplementedError

    @abstractmethod
    def setup(self, generator: DockerCommandScriptGenerator):
        """
        Invoked before container is created.
        """
        raise NotImplementedError

    @abstractmethod
    def teardown(self, generator: DockerCommandScriptGenerator):
        """
        Invoked after container is destroyed.
        """
        raise NotImplementedError
