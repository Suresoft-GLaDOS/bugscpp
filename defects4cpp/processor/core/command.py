from abc import ABCMeta, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import Iterable, List, Type

import message
import taxonomy
from processor.core.argparser import create_taxonomy_parser
from processor.core.docker import Docker, Worktree
from processor.core.shell import Shell


class RegisterCommand(type):
    commands = {}

    def __new__(cls, name, bases, attrs):
        new_class = type.__new__(cls, name, bases, attrs)
        m = attrs["__module__"]
        if m != __name__:
            RegisterCommand.commands[m.split(".")[-1]] = new_class
        return new_class


class CommandMeta(RegisterCommand, ABCMeta):
    pass


class Command(metaclass=CommandMeta):
    @abstractproperty
    def group(self) -> str:
        raise NotImplementedError

    @abstractproperty
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


class DockerCommandLine(metaclass=ABCMeta):
    def __init__(self, commands: List[str]):
        self.commands = commands

    @abstractmethod
    def before(self, info: "DockerExecInfo"):
        """
        Invoked before every time each command is executed.
        """
        raise NotImplementedError

    @abstractmethod
    def after(self, info: "DockerExecInfo"):
        """
        Invoked after every time each command is executed.
        """
        raise NotImplementedError

    def __iter__(self):
        return iter(self.commands)


@dataclass
class DockerExecInfo:
    metadata: taxonomy.MetaData
    worktree: Worktree
    commands: Iterable[DockerCommandLine]
    stream: bool


class DockerCommand(Command):
    def __init__(self):
        pass

    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        info = self.run(argv)
        self.setup(info)
        with Docker(info.metadata.dockerfile, info.worktree) as docker:
            for commands in info.commands:
                commands.before(info)
                for cmd in commands:
                    # Depending on 'stream' value, return value is a bit different.
                    # 'exit_code' is None when 'steam' is True.
                    # https://docker-py.readthedocs.io/en/stable/containers.html
                    exit_code, stream = docker.send(cmd, info.stream)
                    if exit_code is None:
                        for line in stream:
                            message.docker(line.decode("utf-8"))
                commands.after(info)
        self.teardown(info)

    @abstractmethod
    def run(self, argv: List[str]) -> DockerExecInfo:
        raise NotImplementedError

    @abstractmethod
    def setup(self, info: DockerExecInfo):
        raise NotImplementedError

    @abstractmethod
    def teardown(self, info: DockerExecInfo):
        raise NotImplementedError
