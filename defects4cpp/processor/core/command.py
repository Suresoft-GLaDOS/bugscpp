from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Iterable, List, Optional

import message
import taxonomy
from processor.core.docker import Docker, Worktree
from processor.core.shell import Shell


class RegisterCommand(type):
    commands = {}

    def __new__(mcs, name, bases, attrs):
        new_class = type.__new__(mcs, name, bases, attrs)
        m = attrs["__module__"]
        if m != __name__:
            RegisterCommand.commands[m.split(".")[-1]] = new_class
        return new_class


class CommandMeta(RegisterCommand, ABCMeta):
    pass


class Command(metaclass=CommandMeta):
    @property
    def group(self) -> str:
        raise NotImplementedError

    @property
    def help(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def __call__(self, argv: List[str]):
        raise NotImplementedError


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

    def __init__(self, lines: Iterable[str]):
        self.lines = lines

    @abstractmethod
    def before(self, info: "DockerExecInfo"):
        """
        Invoked before script is executed.
        """
        raise NotImplementedError

    @abstractmethod
    def output(self, exit_code: Optional[int], output: str):
        """
        Invoked after each line is executed only if docker is executed with stream set to False.
        """
        pass

    @abstractmethod
    def after(
        self,
        info: "DockerExecInfo",
        exit_code: Optional[int] = None,
        output: Optional[str] = None,
    ):
        """
        Invoked after script is executed.
        """
        raise NotImplementedError

    def __iter__(self):
        return iter(self.lines)


@dataclass
class DockerExecInfo:
    metadata: taxonomy.MetaData
    worktree: Worktree
    scripts: Iterable[DockerCommandScript]
    stream: bool


class DockerCommand(Command):
    """
    Executes each command of DockerCommandLine one by one inside docker container.
    """

    def __init__(self):
        pass

    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        info = self.run(argv)
        self.setup(info)
        with Docker(info.metadata.dockerfile, info.worktree) as docker:
            for script in info.scripts:
                script.before(info)
                for line in script:
                    # Depending on 'stream' value, return value is a bit different.
                    # 'exit_code' is None when 'stream' is True.
                    # https://docker-py.readthedocs.io/en/stable/containers.html
                    exit_code, stream = docker.send(line, info.stream)
                    if exit_code is None:
                        for stream_line in stream:
                            message.docker(stream_line.decode("utf-8", "ignore"))
                    else:
                        script.output(exit_code, stream.decode("utf-8", "ignore"))
                script.after(info)
        self.teardown(info)

    @abstractmethod
    def run(self, argv: List[str]) -> DockerExecInfo:
        """
        Return DockerExecInfo which has information of a command list to run inside docker container.
        """
        raise NotImplementedError

    @abstractmethod
    def setup(self, info: DockerExecInfo):
        """
        Invoked before container is created.
        """
        raise NotImplementedError

    @abstractmethod
    def teardown(self, info: DockerExecInfo):
        """
        Invoked after container is destroyed.
        """
        raise NotImplementedError
