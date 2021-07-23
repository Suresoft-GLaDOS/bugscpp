import argparse
from os import getcwd
from pathlib import Path
from typing import Callable, Iterable, List, Optional, Set

import errors
import message
import taxonomy
from processor.core.argparser import create_common_project_parser, read_config
from processor.core.command import DockerCommand, DockerCommandLine, DockerExecInfo


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
        cases = metadata.defects[index].cases

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


class TestCommandLine(DockerCommandLine):
    """
    Test command
    """

    def __init__(self, commands: Iterable[str], case: int):
        super().__init__(commands)
        self.case = case

    def before(self, info: DockerExecInfo):
        message.info2(f"case #{self.case}")

    def after(self, info: DockerExecInfo):
        pass


class CoverageCommandLine(DockerCommandLine):
    """
    Test command with coverage
    """

    def __init__(self, commands: Iterable[str], case: int, parent: "TestCommand"):
        super().__init__(commands)
        self.case = case
        self.parent = parent

    def before(self, info: DockerExecInfo):
        message.info2(f"case #{self.case}")

    def after(self, info: DockerExecInfo):
        # Callback parent each step.
        self.parent.callback_after(self.case, info)


def _make_coverage_command(
    metadata: taxonomy.MetaData,
) -> Callable[[List[str]], List[str]]:
    """
    Returns gcovr command to run inside docker.
    """

    def coverage_command(commands: List[str]) -> List[str]:
        commands.append(command)
        return commands

    exclude = " ".join([f"--exclude {d}" for d in metadata.common.exclude])
    command = f"gcovr {' '.join(TestCommand.default_options)} {exclude} --root {metadata.common.root}"

    return coverage_command


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
            "--output-directory",
            help="Output directory to place json files",
            type=str,
            dest="output_directory",
            action=ValidateOutputDirectory,
        )
        self.parser.usage = (
            "d++ test --project=[project_name] --no=[number] [--coverage] "
            "--case=[number] [checkout directory]"
        )
        self.coverage: Optional[bool] = None
        self.output_directory: Optional[str] = None
        self.coverage_files: List[str] = []
        self.failed_coverage_files: List[str] = []

    def run(self, argv: List[str]) -> DockerExecInfo:
        args = self.parser.parse_args(argv)
        metadata, worktree = read_config(args.path)

        self.coverage = True if args.coverage else False
        self.output_directory = (
            args.output_directory if args.output_directory else getcwd()
        )

        test_command = (
            metadata.common.test_coverage_command
            if self.coverage
            else metadata.common.test_command
        )
        index = worktree.index

        # Default value is to run all cases.
        selected_defect = metadata.defects[index - 1]
        if not args.case:
            cases = set(range(1, selected_defect.cases + 1))
        else:
            included_cases, excluded_cases = args.case
            if not included_cases:
                included_cases = set(range(1, selected_defect.cases + 1))
            cases = included_cases.difference(excluded_cases)

        filter_command = _make_filter_command(selected_defect)
        if self.coverage:
            coverage_command = _make_coverage_command(metadata)
            command_generator = (
                CoverageCommandLine(
                    coverage_command(
                        [
                            filter_command(case),
                            *test_command,
                        ]
                    ),
                    case,
                    self,
                )
                for case in cases
            )
        else:
            command_generator = (
                TestCommandLine(
                    [
                        filter_command(case),
                        *test_command,
                    ],
                    case,
                )
                for case in cases
            )
        stream = False if args.quiet else True

        return DockerExecInfo(metadata, worktree, command_generator, stream)

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

    def callback_after(self, case: int, info: DockerExecInfo):
        """
        Move json files to somewhere specified by a user or the current working directory.
        Output format:
            {project-name}-{type}#{index}-{case}/summary.json

        Should be invoked only after each coverage command is executed.
        """
        assert self.output_directory

        worktree = info.worktree
        coverage = worktree.host / TestCommand.coverage_output
        summary_dir = (
            Path(self.output_directory)
            / f"{info.metadata.name}-{worktree.suffix}-{case}"
        )
        summary_path = summary_dir / TestCommand.coverage_output

        if coverage.exists():
            summary_dir.mkdir(parents=True, exist_ok=True)
            # TODO: python3.8: Path.rename() returns pathlib.Path
            coverage.rename(summary_path)
            root = info.metadata.common.root
            for gcov_data in worktree.host.glob(f"{root}/**/*.gcov"):
                # FIXME: Possibility to name collision
                gcov_data.rename(f"{summary_dir}/{gcov_data.name}")
            self.coverage_files.append(str(summary_path))
        else:
            self.failed_coverage_files.append(f"{summary_path}")

    @property
    def help(self) -> str:
        return "Run test"
