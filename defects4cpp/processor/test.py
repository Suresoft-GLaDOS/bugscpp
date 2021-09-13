import argparse
import shutil
from os import getcwd
from pathlib import Path
from typing import Iterable, List, NamedTuple, Optional, Set

import errors
import message
import taxonomy
from processor.core.argparser import create_common_project_parser, read_config
from processor.core.command import DockerCommand, DockerCommandScript, DockerExecInfo, Worktree
from taxonomy import MetaData


class ValidateCase(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        """
        case_expression == INCLUDE[:EXCLUDE]
          INCLUDE | EXCLUDE
          * select: ','
          * range:  '-'
        e.g.
          1-100:3,6,7 (to 100 from 1 except 3, 6 and 7)
          20-30,40-88:47-52 (to 30 from 20 and to 88 from 40 except to 62 from 47)
        """

        def expr2set(expr: str) -> Set[int]:
            if not expr:
                return set()
            val: Set[int] = set()
            partitions = expr.split(",")
            for partition in partitions:
                tokens = partition.split("-")
                if len(tokens) == 1:
                    val.add(int(tokens[0]))
                else:
                    val.update(range(int(tokens[0]), int(tokens[1]) + 1))
            return val

        def validate_each_case(max_num_cases: int, case_set: Set[int]) -> Set[int]:
            if all(0 < case <= max_num_cases for case in case_set):
                return case_set
            raise errors.DppInvalidCaseExpressionError(
                index, metadata.name, max_num_cases, values
            )

        try:
            metadata: taxonomy.MetaData = namespace.metadata
            index: int = namespace.worktree.index
        except AttributeError:
            raise errors.DppCaseExpressionInternalError(namespace)

        num_cases = metadata.defects[index - 1].num_cases
        expr_tokens = values.split(":")
        included_cases = validate_each_case(num_cases, expr2set(expr_tokens[0]))
        excluded_cases = validate_each_case(
            num_cases, expr2set(expr_tokens[1]) if len(expr_tokens) > 1 else set()
        )
        setattr(namespace, self.dest, (included_cases, excluded_cases))


class ValidateOutputDirectory(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not Path(values).exists():
            raise errors.DppFileNotFoundError(values)
        setattr(namespace, self.dest, values)


Line = NamedTuple("Line", [("cmd", str), ("save_output", bool)])


class TestCommandScript(DockerCommandScript):
    """
    Script to execute test.
    """

    def __init__(self, script: Iterable[Line], case: int, parent: "TestCommand"):
        super().__init__([line.cmd for line in script])
        self.case = case
        self.parent = parent
        self.current_linenr: int = 1
        self.save_output_linenr = [
            index for index, line in enumerate(script, start=1) if line.save_output
        ]

    def before(self, info: DockerExecInfo):
        message.info2(f"case #{self.case}")

    def output(self, exit_code: int, stream: str):
        if self.current_linenr in self.save_output_linenr:
            self.parent.save_result(
                self.case, True if exit_code == 0 else False, stream
            )
        self.current_linenr += 1

    def after(
        self,
        info: "DockerExecInfo",
        exit_code: Optional[int] = None,
        output: Optional[str] = None,
    ):
        pass


class CoverageCommandScript(TestCommandScript):
    """
    Script to execute test with coverage.
    """

    def __init__(self, script: Iterable[Line], case: int, parent: "TestCommand"):
        super().__init__(script, case, parent)

    def after(
        self,
        info: "DockerExecInfo",
        exit_code: Optional[int] = None,
        output: Optional[str] = None,
    ):
        self.parent.save_coverage(self.case, info)


class CommandScriptGenerator:
    """
    Factory class of CommandScript
    """

    def __init__(
        self,
        parent: "TestCommand",
        defect: taxonomy.Defect,
        metadata: taxonomy.MetaData,
        coverage=False,
    ):
        self._parent = parent
        self._test_type = metadata.common.test_type
        self._defect = defect
        self._gcov = metadata.common.gcov
        self._coverage = coverage

    def _generate_command(self, test_lines: List[Line], case) -> DockerCommandScript:
        if self._coverage:
            test_lines.extend([Line(cmd, False) for cmd in self._gcov.command])
            exclude = " ".join(
                [
                    f"--gcov-exclude {excluded_gcov}"
                    for excluded_gcov in self._gcov.exclude
                ]
            )
            test_lines.append(
                Line(
                    f"gcovr {exclude} --keep --use-gcov-files --json gcov/summary.json gcov",
                    False,
                )
            )
            return CoverageCommandScript(
                test_lines,
                case,
                self._parent,
            )
        else:
            return TestCommandScript(test_lines, case, self._parent)

    def __call__(
        self, cases: Set[int], test_command: List[str]
    ) -> Iterable[DockerCommandScript]:
        """
        Converts integer input appropriately to run a specific test case only inside docker,
        and returns that command.

        For instance, if project uses automake, it returns command that modifies lua script
        which will be used to select which test case to run.
        If it uses ctest, it tries to get a list of test labels via "ctest --show-only=human"
        and select a label at index from top to bottom.
        """
        # Set True to the last command of test_command to save output of the result.
        test_lines: List[Line] = [Line(cmd, False) for cmd in test_command[:-1]]
        test_lines.append(Line(test_command[-1], True))

        if self._test_type == taxonomy.TestType.Automake:
            return (
                self._generate_command(
                    [
                        Line(f"sh -c 'echo {case} > DPP_TEST_INDEX'", False),
                        *test_lines,
                    ],
                    case,
                )
                for case in cases
            )
        elif self._test_type == taxonomy.TestType.CTest:
            return (
                self._generate_command(
                    [
                        Line(f"sh -c 'echo {case} > DPP_TEST_INDEX'", False),
                        *test_lines,
                    ],
                    case,
                )
                for case in cases
            )
        elif self._test_type == taxonomy.TestType.GoogleTest:
            # TODO: generate gtest filter command
            raise NotImplementedError

        raise errors.DppCommandScriptGeneratorInternalError(self._test_type)


class TestCommand(DockerCommand):
    """
    Run test command either with or without coverage.
    """

    def __init__(self):
        super().__init__()
        self.parser = create_common_project_parser()
        self.parser.add_argument(
            "-c",
            "--case",
            help="Index of test cases to run",
            type=str,
            dest="case",
            action=ValidateCase,
        )
        self.parser.add_argument(
            "--output-dir",
            help="Output directory to place json files",
            type=str,
            dest="output_dir",
            action=ValidateOutputDirectory,
        )
        self.parser.usage = (
            "d++ test --project=[project_name] --no=[number] [--coverage] "
            "--case=[number] [checkout directory]"
        )
        self.metadata: Optional[MetaData] = None
        self.worktree: Optional[Worktree] = None
        self.coverage: Optional[bool] = None
        self.output: str = getcwd()
        self.coverage_files: List[str] = []
        self.failed_coverage_files: List[str] = []

    def run(self, argv: List[str]) -> DockerExecInfo:
        args = self.parser.parse_args(argv)
        metadata, worktree = read_config(args.path)
        self.metadata = metadata
        self.worktree = worktree
        self.coverage = True if args.coverage else False
        if args.output_dir:
            self.output = args.output_dir

        test_command = (
            metadata.common.test_coverage_command
            if self.coverage
            else metadata.common.test_command
        )
        index = worktree.index

        # Select cases to run. If none is given, select all.
        selected_defect = metadata.defects[index - 1]
        if not args.case:
            cases = set(range(1, selected_defect.num_cases + 1))
        else:
            included_cases, excluded_cases = args.case
            if not included_cases:
                included_cases = set(range(1, selected_defect.num_cases + 1))
            cases = included_cases.difference(excluded_cases)

        # Generate script to run inside docker.
        writer = CommandScriptGenerator(self, selected_defect, metadata, self.coverage)
        return DockerExecInfo(
            metadata,
            worktree,
            writer(cases, test_command),
            stream=True if args.verbose else False,
        )

    def setup(self, info: DockerExecInfo):
        if not self.coverage:
            message.info(f"Start running {info.metadata.name}")
        else:
            message.info(f"Generating coverage data for {info.metadata.name}")

    def teardown(self, info: DockerExecInfo):
        message.info(f"Finished {info.metadata.name}")
        if self.coverage:
            if self.coverage_files:
                created = [f"    - {c}\n" for c in self.coverage_files]
                message.info2(f"Successfully created:\n{''.join(created)}")
            if self.failed_coverage_files:
                not_created = [f"    - {c}\n" for c in self.failed_coverage_files]
                message.info2(f"Could not create files:\n{''.join(not_created)}")

    def summary_dir(self, case: int) -> Path:
        p = Path(self.output) / f"{self.metadata.name}-{self.worktree.suffix}-{case}"
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        return p

    def save_result(self, case: int, passed: bool, output: str):
        """
        Write exit_code and output to file.
        - {case}.output: contains captured output
        - {case}.test: either 'passed' or 'failed' string.

        Should be invoked only after test command is executed.
        """
        d = self.summary_dir(case)
        with open(d / f"{case}.output", "w+") as output_file:
            output_file.write(output)
        with open(d / f"{case}.test", "w+") as result_file:
            result_file.write("passed" if passed else "failed")

    def save_coverage(self, case: int, info: DockerExecInfo):
        """
        Move json files to somewhere specified by a user or the current working directory.
        Output format:
            {project-name}-{type}#{index}-{case}/summary.json

        Should be invoked only after each coverage command is executed.
        """
        worktree = info.worktree
        coverage = worktree.host / "gcov"
        coverage_dest = self.summary_dir(case)

        if coverage.exists():
            for file in coverage.glob("*"):
                # Full path should be passed to overwrite if already exists.
                shutil.move(str(file), str(coverage_dest / file.name))
            else:
                coverage.rmdir()
        else:
            self.failed_coverage_files.append(str(coverage_dest / coverage.name))

    @property
    def help(self) -> str:
        return "Run test"
