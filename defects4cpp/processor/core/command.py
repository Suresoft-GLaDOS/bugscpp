import argparse
from abc import ABCMeta, abstractmethod, abstractproperty
from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Set, Type

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


class TestCommandMixinLine(DockerCommandLine):
    def __init__(self, commands: Iterable[str], case: int):
        self.commands = commands
        self.case = case


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
    def __init__(self, instance: Type[TestCommandMixinLine] = TestCommandMixinLine):
        super().__init__()
        self.instance = instance
        self.parser = create_taxonomy_parser()
        self.parser.add_argument(
            "-c",
            "--case",
            help="Index of test cases to run",
            type=str,
            dest="case",
            action=ValidateCase,
        )

    def generate(self, argv: List[str], coverage=False) -> DockerExecInfo:
        args = self.parser.parse_args(argv)
        metadata: taxonomy.MetaData = args.metadata
        test_command = (
            metadata.common.test_cov_command
            if coverage
            else metadata.common.test_command
        )
        index = args.index

        # Default value is to run all cases.
        selected_defect = metadata.defects[index - 1]
        if not args.case:
            cases = set(range(1, selected_defect.cases + 1))
        else:
            included_cases, excluded_cases = args.case
            if not included_cases:
                included_cases = set(range(1, selected_defect.cases + 1))
            cases = included_cases.difference(excluded_cases)

        filter_command = self._make_filter_command(selected_defect)
        if type(self).each_command is __class__.each_command:
            generator = (
                self.instance(
                    [
                        filter_command(case),
                        *test_command,
                    ],
                    case,
                )
                for case in cases
            )
        else:
            generator = (
                self.instance(
                    self.each_command(
                        [
                            filter_command(case),
                            *test_command,
                        ]
                    ),
                    case,
                )
                for case in cases
            )
        stream = False if args.quiet else True

        return DockerExecInfo(metadata, args.worktree, generator, stream)

    @abstractmethod
    def each_command(self, commands: List[str]) -> List[str]:
        """
        Override this method to hook each command line.
        """
        pass

    def _make_filter_command(self, defect: taxonomy.Defect) -> Callable[[int], str]:
        """
        Returns command to run inside docker that modifies lua script return value which will be used to select which test case to run.

        Assume that "split.patch" newly creates "defects4cpp.lua" file.
        Read "split.patch" and get line containing "create mode ... defects4cpp.lua"
        This should retrieve the path to "defects4cpp.lua" relative to the project directory.
        """

        def filter_command(case: int) -> str:
            return f"bash -c 'echo return {case} > {lua_path}'"

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

        return filter_command
