"""
Test command.

Run tests of the project inside a container.
"""
import argparse
import shutil
from dataclasses import dataclass
from os import getcwd, system
from pathlib import Path
from textwrap import dedent
from typing import Callable, Generator, List, Optional, Set, Union, cast

from config import config
from errors import (DppAdditionalGcovOptionsWithoutCoverage, DppArgparseFileNotFoundError,
                    DppCaseExpressionInternalError)
from errors.argparser import DppArgparseInvalidCaseExpressionError
from message import message
from processor.core.argparser import create_common_project_parser
from processor.core.command import DockerCommand, DockerCommandScript, DockerCommandScriptGenerator
from processor.core.data import Worktree
from taxonomy import Command, CommandType, Defect, MetaData


class AdditionalGcovOptions(argparse.Action):
    """
    Additional options for gcov command.
    """

    def __call__(self, parser, namespace, values, option_string=None):
        config.DPP_ADDITIONAL_GCOV_OPTIONS = values
        setattr(namespace, self.dest, values)


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
            raise DppArgparseInvalidCaseExpressionError(
                index, metadata.name, max_num_cases, values
            )

        try:
            metadata: MetaData = namespace.metadata
            index: int = namespace.worktree.index
        except AttributeError:
            raise DppCaseExpressionInternalError(namespace)

        num_cases = metadata.defects[index - 1].num_cases
        expr_tokens = values.split(":")
        included_cases = validate_each_case(num_cases, expr2set(expr_tokens[0]))
        excluded_cases = validate_each_case(
            num_cases, expr2set(expr_tokens[1]) if len(expr_tokens) > 1 else set()
        )
        setattr(namespace, self.dest, (included_cases, excluded_cases))


class ValidateOutputDirectory(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        Path(values).mkdir(parents=True, exist_ok=True)
        setattr(namespace, self.dest, values)


class ObservableAttributeMeta(type):
    def __new__(mcs, name, bases, attr, methods=None):
        if methods is None:
            methods = []
        for method in methods:
            attr[method] = mcs.wrap(attr[method])
        return super().__new__(mcs, name, bases, attr)

    @classmethod
    def wrap(mcs, fn):
        def update(obj, *args, **kwargs):
            output = fn(obj, *args, **kwargs)
            for callback in obj.callbacks:
                callback(*args, **kwargs)
            return output

        return update


class ObservableAttribute(metaclass=ObservableAttributeMeta):
    def __init__(self, callbacks: List[Callable]):
        self._callbacks = callbacks

    @property
    def callbacks(self):
        return self._callbacks


class ManagedAttribute(ObservableAttribute, methods=["__set__"]):
    def __set_name__(self, owner, name):
        self.name = f"_{name}"

    def __get__(self, instance, owner):
        return getattr(instance, self.name)

    def __set__(self, instance, value):
        setattr(instance, self.name, value)


@dataclass
class CapturedOutput:
    exit_code: int
    stream: str


class CapturedOutputAttributeMixin:
    _captured_output: Optional[Union[ManagedAttribute, CapturedOutput]] = None

    @property
    def captured_output(self) -> CapturedOutput:
        return self._captured_output

    @captured_output.setter
    def captured_output(self, value):
        self._captured_output = value


class TestCommandScript(DockerCommandScript, CapturedOutputAttributeMixin):
    """
    Script to execute test.
    """

    __test__ = False

    def __init__(
        self,
        case: int,
        command_type: CommandType,
        command: List[str],
    ):
        super().__init__(command_type, command)
        self._case = case

    @property
    def case(self) -> int:
        return self._case

    def before(self):
        message.stdout_progress_detail(f"case #{self._case}")

    def step(self, linenr: int, line: str):
        pass

    def output(self, linenr: Optional[int], exit_code: int, output: str):
        if linenr == len(self.lines):
            self.captured_output = CapturedOutput(exit_code, output)

    def after(self):
        pass


class SetupTestCommandScript(TestCommandScript):
    """
    Script to execute before running actual code.

    It prepends an extra command which writes an index number to file addition to the given commands.
    It is script's responsibility to read the file and parse into appropriate filter name.
    For instance, if the test is automake-generated, it might convert the number into 'TESTS' value.
    If the test is cmake-generated, it might convert the number into regex value of '--tests-regex'.
    """

    OUTPUT_NAME = "DPP_TEST_INDEX"

    def __init__(
        self,
        case: int,
    ):
        super().__init__(
            case,
            CommandType.Docker,
            [f"sh -c 'echo {case} > {SetupTestCommandScript.OUTPUT_NAME}'"],
        )

    def before(self):
        # Override TestCommandScript.before method to prevent echoing.
        pass


class CoverageTestCommandScript(TestCommandScript):
    """
    Script to execute test with coverage.
    """

    def __init__(
        self,
        case: int,
        command_type: CommandType,
        command: List[str],
    ):
        super().__init__(case, command_type, command)


class TeardownTestCommandScript(TestCommandScript):
    """
    Script to execute after running CoverageTestCommandScript.

    Clear the coverage data by remove gcov directory and its contents.
    related to: https://github.com/Suresoft-GLaDOS/defects4cpp/issues/66
    """

    __test__ = False

    def __init__(
        self,
        case: int,
    ):
        super().__init__(
            case,
            CommandType.Docker,
            ["sh -c 'rm -rf gcov'"],
        )

    def before(self):
        # Override TestCommandScript.before method to prevent echoing.
        pass


class GcovCommandScript(DockerCommandScript, CapturedOutputAttributeMixin):
    """
    Script to execute gcov.
    """

    def __init__(
        self,
        case: int,
        command_type: CommandType,
        command: List[str],
    ):
        super().__init__(command_type, command)
        self._case = case

    @property
    def case(self) -> int:
        return self._case

    def before(self):
        pass

    def step(self, linenr: int, line: str):
        pass

    def output(self, linenr: Optional[int], exit_code: Optional[int], output: str):
        if linenr == len(self.lines):
            self.captured_output = CapturedOutput(exit_code, output)

    def after(self):
        pass


class RunGcovrTestCommandScript(TestCommandScript):
    """
    Script to execute gcovr to make summary.json.

    Clear the coverage data by remove gcov directory and its contents.
    related to: https://github.com/Suresoft-GLaDOS/defects4cpp/issues/66
    """

    def before(self):
        pass

    def __init__(
        self,
        case: int,
        exclude: List[str],
    ):
        exclude_flags = " ".join(
            [f"--gcov-exclude {excluded_gcov}" for excluded_gcov in exclude]
        )
        super().__init__(
            case,
            CommandType.Docker,
            [
                f"gcovr {exclude_flags} --keep --use-gcov-files --json-pretty --json gcov/summary.json gcov",
                f"gcovr {exclude_flags} --keep --use-gcov-files --html gcov/summary.html gcov",
            ],
        )


class TestCommandScriptGenerator(DockerCommandScriptGenerator):
    """
    Factory class of CommandScript
    """

    __test__ = False

    def __init__(
        self,
        defect: Defect,
        coverage: bool,
        test_command: List[Command],
        test_cases: Set[int],
        callbacks: List[Callable],
        metadata: MetaData,
        worktree: Worktree,
        stream: bool,
    ):
        super().__init__(metadata, worktree, stream)
        self._defect = defect
        self._coverage = coverage
        self._test_command = test_command
        self._test_cases = test_cases
        self._callbacks = callbacks
        self._extra_tests = defect.extra_tests
        self._gcov = metadata.common_gcov_replaced.gcov

    def create(self) -> Generator[TestCommandScript, None, None]:
        self._attach(CapturedOutputAttributeMixin, "_captured_output")

        if self._coverage:
            yield from self._create_coverage_impl()
        else:
            yield from self._create_impl()

    def _attach(self, klass, field_name: str):
        descriptor = ManagedAttribute(self._callbacks)
        setattr(klass, field_name, descriptor)
        descriptor.__set_name__(klass, field_name)

    def _create_impl(self) -> Generator[TestCommandScript, None, None]:
        for case in sorted(self._test_cases):
            yield SetupTestCommandScript(case)
            test_cmd = (
                self._test_command
                if case <= self._defect.num_cases - len(self._extra_tests)
                else self._extra_tests[
                    case - self._defect.num_cases + len(self._extra_tests) - 1
                ]
            )
            for t in test_cmd:
                yield TestCommandScript(case, t.type, t.lines)

    def _create_coverage_impl(self) -> Generator[TestCommandScript, None, None]:
        for case in sorted(self._test_cases):
            yield SetupTestCommandScript(case)
            test_cmd = (
                self._test_command
                if case <= self._defect.num_cases - len(self._extra_tests)
                else self._extra_tests[
                    case - self._defect.num_cases + len(self._extra_tests) - 1
                ]
            )
            for t in test_cmd:
                yield CoverageTestCommandScript(case, t.type, t.lines)
            for gcov_cmd in self._gcov.command:
                yield GcovCommandScript(case, gcov_cmd.type, gcov_cmd.lines)
                yield RunGcovrTestCommandScript(case, self._gcov.exclude)
            yield TeardownTestCommandScript(case)


class TestCommand(DockerCommand):
    """
    Run test command either with or without coverage.
    """

    __test__ = False

    def __init__(self):
        super().__init__(parser=create_common_project_parser())
        # TODO: write argparse description in detail
        self.parser.add_argument(
            "-c",
            "--case",
            help="expression to filter cases (see `example <case-example_>`_)",
            type=str,
            dest="case",
            action=ValidateCase,
        )
        self.parser.add_argument(
            "--output-dir",
            help="output directory to generate coverage data instead of the current directory.",
            type=str,
            dest="output_dir",
            action=ValidateOutputDirectory,
        )
        self.parser.add_argument(
            "--additional-gcov-options",
            type=str,
            dest="additional_gcov_options",
            action=AdditionalGcovOptions,
            help="set additional options to gcov command",
        )
        self.parser.usage = (
            "bugcpp.py test PATH [-j|--jobs=JOBS] "
            "[--coverage [--additional-gcov-options=ADDITIONAL_GCOV_OPTIONS]] "
            "[-v|--verbose] [-c|--case=expr] [--output-dir=directory]"
        )
        self.parser.description = dedent(
            """\
        Run testsuite inside docker. The project must have been built previously.
        """
        )
        self.metadata: Optional[MetaData] = None
        self.worktree: Optional[Worktree] = None
        self.coverage: Optional[bool] = None
        self.output: str = getcwd()
        self.coverage_files: List[str] = []
        self.failed_coverage_files: List[str] = []

    def create_script_generator(
        self, args: argparse.Namespace
    ) -> DockerCommandScriptGenerator:
        if not args.coverage and args.additional_gcov_options:
            raise DppAdditionalGcovOptionsWithoutCoverage()
        metadata = self.metadata = args.metadata
        worktree = self.worktree = args.worktree
        self.coverage = True if args.coverage else False
        if args.output_dir:
            self.output = args.output_dir

        # FIXME: metadata's values are fixed when metadata.commonXXXX is called
        #        When we call metadata.common after calling metadata.common_gcov_replace,
        #        metadata.common.gcov_replace.gcov will not not replaced
        test_command = (
            metadata.common_gcov_replaced.test_coverage_command
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

        return TestCommandScriptGenerator(
            selected_defect,
            self.coverage,
            test_command,
            cases,
            [self.script_callback],
            metadata,
            worktree,
            stream=True if args.verbose else False,
        )

    def setup(self, generator: DockerCommandScriptGenerator):
        message.info(__name__, f"'{generator.metadata.name}'")
        if not self.coverage:
            message.stdout_progress(f"[{generator.metadata.name}] running test suites")
        else:
            message.stdout_progress(
                f"[{generator.metadata.name}] running test suites (coverage)"
            )

    def teardown(self, generator: DockerCommandScriptGenerator):
        message.info(__name__, "done")
        message.stdout_progress(f"[{generator.metadata.name}] done")
        if self.coverage:
            if self.coverage_files:
                created = [f"    - {c}\n" for c in self.coverage_files]
                message.stdout_progress_detail(
                    f"Successfully created:\n{''.join(created)}"
                )
            if self.failed_coverage_files:
                not_created = [f"    - {c}\n" for c in self.failed_coverage_files]
                message.stdout_progress_detail(
                    f"Could not create files:\n{''.join(not_created)}"
                )

    def summary_dir(self, case: int) -> Path:
        """
        Return path where coverage data should be created.

        Parameters
        ----------
        case : int
            Case number.

        Returns
        -------
        pathlib.Path
        """
        p = Path(self.output) / f"{self.metadata.name}-{self.worktree.suffix}-{case}"
        if not p.exists():
            p.mkdir(parents=True, exist_ok=True)
        return p

    def script_callback(self, script: TestCommandScript, *args, **kwargs):
        """
        Callback function to register used to collect data after each command is executed.

        Parameters
        ----------
        script : TestCommandScript
            Script instance which has been executed.

        Returns
        -------
        None
        """
        if (
            type(script) is TestCommandScript
            or type(script) is CoverageTestCommandScript
        ):
            self._save_result(script)
        elif type(script) is RunGcovrTestCommandScript:
            self._save_coverage(cast(GcovCommandScript, script))
        else:
            pass

    def _save_result(self, script: TestCommandScript):
        """
        Write exit code and captured stdout to file.

        - {case}.output: contains captured output
        - {case}.test: either 'passed' or 'failed' string.

        It should be invoked only after test command is executed.

        Parameters
        ----------
        script : TestCommandScript
            Script instance which has been executed.

        Returns
        -------
        None
        """
        d = self.summary_dir(script.case)
        with open(d / f"{script.case}.output", "w+", encoding="utf-8") as output_file:
            output_file.write(script.captured_output.stream)
        with open(d / f"{script.case}.test", "w+", encoding="utf-8") as result_file:
            result_file.write(
                "passed" if script.captured_output.exit_code == 0 else "failed"
            )

    def _save_coverage(self, script: GcovCommandScript):
        """
        Move json files to the target directory, and create summary.json file.
        Output format should be the following:
            {project-name}-{type}#{index}-{case}/summary.json

        It should be invoked only after each coverage command is executed.

        Parameters
        ----------
        script : GcovCommandScript
            Script instance which has been executed.

        Returns
        -------
        None
        """
        coverage = self.worktree.host / "gcov"
        coverage_dest = self.summary_dir(script.case)

        if coverage.exists():
            for file in coverage.glob("*"):
                # Full path should be passed to overwrite if already exists.
                try:
                    shutil.move(str(file), str(coverage_dest / file.name))
                except PermissionError:
                    print(f"PermissionError: {file}")
                    # FIXME: Is this the right way to handle this?
                    system(f"sudo mv {str(file)} {str(coverage_dest / file.name)}")
                    continue
            else:
                # Do not rmdir (TeardownTestCommandScript will do)
                # related to https://github.com/Suresoft-GLaDOS/defects4cpp/issues/66
                self.coverage_files.append(str(coverage_dest / coverage.name))
        else:
            self.failed_coverage_files.append(str(coverage_dest / coverage.name))

    @property
    def help(self) -> str:
        return "Run test"
