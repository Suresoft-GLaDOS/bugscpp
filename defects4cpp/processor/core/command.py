from abc import ABCMeta, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import List

import message
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


@dataclass
class DockerCommandArguments:
    dockerfile: str
    worktree: Worktree
    commands: List[str]


class DockerCommand(Command):
    def __init__(self):
        pass

    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        self.setup()
        docker_args = self.run(argv)
        with Docker(docker_args.dockerfile, docker_args.worktree) as docker:
            for command in docker_args.commands:
                _, stream = docker.send(command)
                for line in stream:
                    message.docker(line.decode("utf-8"))
        self.teardown()

    @abstractmethod
    def run(self, argv: List[str]) -> DockerCommandArguments:
        raise NotImplementedError

    @abstractmethod
    def setup(self) -> DockerCommandArguments:
        raise NotImplementedError

    @abstractmethod
    def teardown(self) -> DockerCommandArguments:
        raise NotImplementedError
