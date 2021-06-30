from abc import ABCMeta, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import List

from processor.core.argparser import TaxonomyParser
from processor.core.docker import Docker
from processor.core.shell import Shell
from taxonomy import MetaData


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


class SimpleCommand(Command):
    @property
    def group(self) -> str:
        return "v1"

    @abstractmethod
    def run(self) -> bool:
        raise NotImplementedError

    def __call__(self) -> bool:
        return self.run()


@dataclass
class ShellCommandArguments:
    commands: List[str]


class ShellCommand(Command):
    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        taxonomy = self.parser(argv)
        args = self.run(taxonomy.metadata, taxonomy.index, taxonomy.buggy)
        with Shell() as shell:
            shell.send(args.commands)

    @abstractmethod
    def run(self, metadata: MetaData, index: int, buggy: bool) -> ShellCommandArguments:
        raise NotImplementedError

    @abstractproperty
    def parser(self) -> TaxonomyParser:
        raise NotImplementedError


@dataclass
class DockerCommandArguments:
    commands: List[str]


class DockerCommand(Command):
    @property
    def group(self) -> str:
        return "v1"

    def __call__(self, argv: List[str]):
        taxonomy = self.parser(argv)
        args = self.run(taxonomy.metadata, taxonomy.index, taxonomy.buggy)

        with Docker(
            taxonomy.metadata.dockerfile,
            "/home/haku/workspace/github/defects4cpp/home",
            "/workspace",
        ) as docker:
            docker.send(args.commands)

    @abstractmethod
    def run(
        self, metadata: MetaData, index: int, buggy: bool
    ) -> DockerCommandArguments:
        raise NotImplementedError

    @abstractproperty
    def parser(self) -> TaxonomyParser:
        raise NotImplementedError
