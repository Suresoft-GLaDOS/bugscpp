import argparse
from os import getcwd
from pathlib import Path
from typing import List

import message
from processor.core.command import TestCommandMixin, DockerCommand, DockerCommandArguments
from processor.core.docker import Worktree
from processor.test import TestCommand, ValidateCase
from taxonomy import MetaData


class ValidateTest(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)


class CoverageCommand(TestCommandMixin, DockerCommand):
    """
    Run test and generate coverage data.
    """

    def __init__(self):
        super().__init__()
        self.parser.usage = (
            "d++ build --project=[project_name] --no=[number] --case=[index] [checkout directory]"
        )
        self.parser.add_argument(
            "--test",
            help="Run test and coverage at once",
            dest="test",
            nargs=0,
            action=ValidateTest,
        )

    def run(self, argv: List[str]) -> DockerCommandArguments:
        args = self.parser.parse_args(argv)
        commands = []
        if args.test:
            commands.extend(self.generate_test_command(argv).commands)

        metadata: MetaData = args.metadata
        self._coverage_name: str = f"{Path(args.worktree.host).stem}.json"
        self._worktree: Worktree = args.worktree

        exclude_options = [f"--gcov-exclude {dir}" for dir in metadata.common.exclude]
        options = ["--print-summary", "--delete", "--json", self._coverage_name]
        commands.append(
            f"gcovr -r {metadata.common.root} {' '.join(exclude_options)} {' '.join(options)}"
        )

        message.info(
            f"Generating coverage data for {metadata.name} {self._coverage_name}"
        )
        return DockerCommandArguments(metadata.dockerfile, self._worktree, commands)

    def setup(self):
        pass

    def teardown(self):
        assert self._coverage_name and self._worktree

        coverage = Path(self._worktree.host) / self._coverage_name
        if not coverage.exists():
            message.warning(
                f"Failed to generate coverage data. {self._coverage_name} is not created"
            )
            return

        coverage = coverage.rename(f"{getcwd()}/{self._coverage_name}")
        message.info(f"{self._coverage_name} is created at {str(coverage)}")

    @property
    def help(self) -> str:
        return "Coverage build local with a build tool from docker"
