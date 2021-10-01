import argparse
import shutil
from dataclasses import dataclass
from os import getcwd
from pathlib import Path
from typing import Callable, Generator, List, Optional, Set, Union

import errors
import message
import taxonomy
from processor.core.argparser import create_common_project_parser, read_config
from processor.core.command import DockerCommand, DockerCommandScript, DockerCommandScriptGenerator, Worktree
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


class MetaObservableAttribute(type):
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


class ObservableAttribute(metaclass=MetaObservableAttribute):
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

    def __init__(
        self,
        case: int,
        command_type: taxonomy.CommandType,
        command: List[str],
    ):
        super().__init__(command_type, command)
        self._case = case

    @property
    def case(self) -> int:
        return self._case

    def before(self):
        message.info2(f"case #{self._case}")

    def output(self, linenr: int, exit_code: int, output: str):
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
            taxonomy.CommandType.Docker,
            [f"sh -c 'echo {case} > {SetupTestCommandScript.OUTPUT_NAME}'"],
        )


class CoverageTestCommandScript(TestCommandScript):
    """
    Script to execute test with coverage.
    """

    def __init__(
        self,
        case: int,
        command_type: taxonomy.CommandType,
        command: List[str],
    ):
        super().__init__(case, command_type, command)


class GcovCommandScript(DockerCommandScript, CapturedOutputAttributeMixin):
    """
    Script to execute gcov.
    """

    def __init__(
        self, exclude: List[str], command_type: taxonomy.CommandType, command: List[str]
    ):
        exclude_flags = " ".join(
            [f"--gcov-exclude {excluded_gcov}" for excluded_gcov in exclude]
        )
        command.append(
            f"gcovr {exclude_flags} --keep --use-gcov-files --json --output gcov/summary.json gcov"
        )
        super().__init__(command_type, command)

    def before(self):
        pass

    def output(self, linenr, exit_code: Optional[int], output: str):
        if linenr == len(self.lines):
            self.captured_output = CapturedOutput(exit_code, output)

    def after(self):
        pass


class TestCommandScriptGenerator(DockerCommandScriptGenerator):
    """
    Factory class of CommandScript
    """

    def __init__(
        self,
        defect: taxonomy.Defect,
        coverage: bool,
        test_command: taxonomy.Command,
        test_cases: Set[int],
        callbacks: List[Callable],
        metadata: taxonomy.MetaData,
        worktree: Worktree,
        stream: bool,
    ):
        super().__init__(metadata, worktree, stream)
        self._defect = defect
        self._coverage = coverage
        self._test_command = test_command
        self._test_cases = test_cases
        self._callbacks = callbacks
        self._gcov = metadata.common.gcov

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

    def _create_impl(self) -> Generator[CoverageTestCommandScript, None, None]:
        for case in sorted(self._test_cases):
            yield SetupTestCommandScript(case)
            yield TestCommandScript(
                case,
                self._test_command.type,
                self._test_command.lines,
            )

    def _create_coverage_impl(self) -> Generator[TestCommandScript, None, None]:
        for case in sorted(self._test_cases):
            yield SetupTestCommandScript(case)
            yield CoverageTestCommandScript(
                case,
                self._test_command.type,
                self._test_command.lines,
            )
            yield GcovCommandScript(
                self._gcov.exclude, self._gcov.command.type, self._gcov.command.lines
            )


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

    def create_script_generator(self, argv: List[str]) -> DockerCommandScriptGenerator:
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
        if not self.coverage:
            message.info(f"Start running {generator.metadata.name}")
        else:
            message.info(f"Generating coverage data for {generator.metadata.name}")

    def teardown(self, generator: DockerCommandScriptGenerator):
        message.info(f"Finished {generator.metadata.name}")
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

    def script_callback(self, script: TestCommandScript, *args, **kwargs):
        if type(script) is TestCommandScript:
            self._save_result(script)
        elif type(script) is CoverageTestCommandScript:
            self._save_coverage(script)
        else:
            pass

    def _save_result(self, script: TestCommandScript):
        """
        Write exit_code and output to file.
        - {case}.output: contains captured output
        - {case}.test: either 'passed' or 'failed' string.

        Should be invoked only after test command is executed.
        """
        d = self.summary_dir(script.case)
        with open(d / f"{script.case}.output", "w+") as output_file:
            output_file.write(script.captured_output.stream)
        with open(d / f"{script.case}.test", "w+") as result_file:
            result_file.write(
                "passed" if script.captured_output.exit_code == 0 else "failed"
            )

    def _save_coverage(self, script: CoverageTestCommandScript):
        """
        Move json files to somewhere specified by a user or the current working directory.
        Output format:
            {project-name}-{type}#{index}-{case}/summary.json

        Should be invoked only after each coverage command is executed.
        """
        coverage = self.worktree.host / "gcov"
        coverage_dest = self.summary_dir(script.case)

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
