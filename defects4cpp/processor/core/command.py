import argparse
from abc import ABCMeta, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import List, Optional, Set

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


class ValidateCase(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        """
        case == INCLUDE[:EXCLUDE]
          INCLUDE | EXCLUDE
          * select: ','
          * range:  '-'
        e.g.
          1-100:3,6,7 (to 100 from 1 except 3, 6 and 7)
          20-30,40-88:47-52 (to 30 from 20 and to 88 from 40 except to 62 from 47)
        """

        def select_cases(expr: str) -> Set[int]:
            if not expr:
                return set()
            cases: Set[int] = set()
            partitions = expr.split(",")
            for partition in partitions:
                tokens = partition.split("-")
                if len(tokens) == 1:
                    cases.add(int(tokens[0]))
                else:
                    cases.update(range(int(tokens[0]), int(tokens[1]) + 1))
            return cases

        values = values.split(":")
        included_cases = select_cases(values[0])
        excluded_cases = select_cases(values[1]) if len(values) > 1 else set()
        # TODO: the range must be validated by taxonomy lookup.
        setattr(namespace, self.dest, (included_cases, excluded_cases))


class TestCommandMixin(Command):
    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.add_argument(
            "-c",
            "--case",
            help="Index of test cases to run",
            type=str,
            dest="case",
            action=ValidateCase,
        )

    def generate_test_command(self, argv: List[str]) -> DockerCommandArguments:
        args = self.parser.parse_args(argv)
        metadata: taxonomy.MetaData = args.metadata
        index = args.index
        worktree = args.worktree

        # Default value is to run all cases.
        commands = []
        selected_defect = metadata.defects[index - 1]
        if not args.case:
            cases = set(range(1, selected_defect.cases + 1))
        else:
            included_cases, excluded_cases = args.case
            if not included_cases:
                included_cases = set(range(1, selected_defect.cases + 1))
            cases = included_cases.difference(excluded_cases)
        # TODO: refactoring
        for case in cases:
            commands.append(self._select_index(selected_defect, case))
            commands.append(*metadata.common.test_command)

        message.info(f"Running {metadata.name} test")
        return DockerCommandArguments(metadata.dockerfile, worktree, commands)

    def _select_index(self, defect: taxonomy.Defect, case_index: int):
        """
        Returns command to run inside docker that modifies lua script return value which will be used to select which test case to run.

        Assume that "split.patch" newly creates "defects4cpp.lua" file.
        Read "split.patch" and get line containing "create mode ... defects4cpp.lua"
        This should retrieve the path to "defects4cpp.lua" relative to the project directory.
        """
        with open(defect.split_patch) as fp:
            lines = [line for line in fp if "create mode" in line]

        lua_path: Optional[str] = None
        for line in lines:
            if "defects4cpp.lua" in line:
                # "create mode number filename"[-1] == filename
                lua_path = line.split()[-1]
                break
        if not lua_path:
            raise AssertionError(f"could not get lua_path in {defect.split_patch}")
        return f"bash -c 'echo return {case_index} > {lua_path}'"
