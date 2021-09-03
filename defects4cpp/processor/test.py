import argparse
from os import getcwd
from pathlib import Path
from typing import Callable, Iterable, List, NamedTuple, Optional, Set

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

        def validate_each_case(case_set: Set[int]) -> Set[int]:
            if all(0 < case < cases for case in case_set):
                return case_set
            raise errors.DppInvalidCaseExpressionError(
                index, metadata.name, cases, values
            )

        try:
            metadata: taxonomy.MetaData = namespace.metadata
            index: int = namespace.worktree.index
        except AttributeError:
            raise errors.DppCaseExpressionInternalError(namespace)
        cases = metadata.defects[index - 1].cases

        expr_tokens = values.split(":")
        included_cases = validate_each_case(expr2set(expr_tokens[0]))
        excluded_cases = validate_each_case(
            expr2set(expr_tokens[1]) if len(expr_tokens) > 1 else set()
        )
        setattr(namespace, self.dest, (included_cases, excluded_cases))


class ValidateOutputDirectory(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not Path(values).exists():
            raise errors.DppFileNotFoundError(values)
        setattr(namespace, self.dest, values)


Line = NamedTuple("Line", [("line", str), ("save_output", bool)])


def _make_filter_command(defect: taxonomy.Defect) -> Callable[[int], str]:
    """
    Returns command to run inside docker that modifies lua script 'return value'
    which will be used to select which test case to run.

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
        raise errors.DppPatchError(defect)
    return filter_command


class TestCommandScript(DockerCommandScript):
    """
    Script to execute test.
    """

    def __init__(self, script: Iterable[Line], case: int, parent: "TestCommand"):
        super().__init__([line.line for line in script])
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

    def after(self, info: DockerExecInfo):
        pass


class TestCommandScriptGenerator:
    """
    Factory class of TestComandScript
    """

    def __init__(self, parent: "TestCommand", defect: taxonomy.Defect):
        self._parent = parent
        self._filter_command = _make_filter_command(defect)

    def __call__(
        self, cases: Set[int], test_command: List[str]
    ) -> Iterable[DockerCommandScript]:
        """
        Set True to the last command of test_command.
        """
        test_lines: List[Line] = [Line(cmd, False) for cmd in test_command[:-1]]
        test_lines.append(Line(test_command[-1], True))
        return (
            TestCommandScript(
                [Line(self._filter_command(case), False), *test_lines],
                case,
                self._parent,
            )
            for case in cases
        )


class CoverageCommandScript(TestCommandScript):
    """
    Script to execute test with coverage.
    """

    def __init__(self, script: Iterable[Line], case: int, parent: "TestCommand"):
        super().__init__(script, case, parent)

    def after(self, info: DockerExecInfo):
        self.parent.save_coverage(self.case, info)


class CoverageCommandScriptGenerator:
    """
    Factory class of CoverageCommandScript
    """

    def __init__(
        self,
        parent: "TestCommand",
        defect: taxonomy.Defect,
        metadata: taxonomy.MetaData,
    ):
        self._parent = parent
        self._filter_command = _make_filter_command(defect)
        exclude = " ".join([f"--exclude {d}" for d in metadata.common.exclude])
        self._coverage_command: Line = Line(
            f"gcovr {' '.join(TestCommand.default_options)} {exclude} --root {metadata.common.root}",
            False,
        )

    def __call__(
        self, cases: Set[int], test_command: List[str]
    ) -> Iterable[DockerCommandScript]:
        """
        Set True to the last command of test_command.
        """
        test_lines: List[Line] = [Line(cmd, False) for cmd in test_command[:-1]]
        test_lines.append(Line(test_command[-1], True))
        return (
            CoverageCommandScript(
                [
                    Line(self._filter_command(case), False),
                    *test_lines,
                    self._coverage_command,
                ],
                case,
                self._parent,
            )
            for case in cases
        )


class TestCommand(DockerCommand):
    """
    Run test command either with or without coverage.
    """

    coverage_output = "summary.json"
    default_options = [
        "--print-summary",
        "--delete",
        "--keep",
        "--html",
        "result.html",
        "--json",
        coverage_output,
    ]

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
            cases = set(range(1, selected_defect.cases + 1))
        else:
            included_cases, excluded_cases = args.case
            if not included_cases:
                included_cases = set(range(1, selected_defect.cases + 1))
            cases = included_cases.difference(excluded_cases)

        # Generate script to run inside docker.
        writer = (
            CoverageCommandScriptGenerator(self, selected_defect, metadata)
            if self.coverage
            else TestCommandScriptGenerator(self, selected_defect)
        )

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
        dir = self.summary_dir(case)
        with open(dir / f"{case}.output", "w+") as output_file:
            output_file.write(output)
        with open(dir / f"{case}.test", "w+") as result_file:
            result_file.write("passed" if passed else "failed")

    def save_coverage(self, case: int, info: DockerExecInfo):
        """
        Move json files to somewhere specified by a user or the current working directory.
        Output format:
            {project-name}-{type}#{index}-{case}/summary.json

        Should be invoked only after each coverage command is executed.
        """
        worktree = info.worktree
        coverage = worktree.host / TestCommand.coverage_output
        coverage_dest = self.summary_dir(case)

        if coverage.exists():
            # TODO: python3.8: Path.rename() returns pathlib.Path
            coverage.rename(coverage_dest / coverage.name)
            root = info.metadata.common.root
            for gcov_data in worktree.host.glob(f"{root}/**/*.gcov"):
                # FIXME: Possibility to name collision
                gcov_data.rename(f"{coverage_dest}/{gcov_data.name}")
            self.coverage_files.append(str(coverage))
        else:
            self.failed_coverage_files.append(str(coverage))

    @property
    def help(self) -> str:
        return "Run test"
