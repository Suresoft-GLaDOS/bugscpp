import argparse
from os import getcwd
from typing import List

import message
from processor.core.command import (DockerCommand, DockerCommandLine, DockerExecInfo, TestCommandMixin,
                                    TestCommandMixinLine)


class ValidateTest(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, True)


class CoverageCommandLine(TestCommandMixinLine):
    def before(self, info: DockerExecInfo):
        message.info2(f"case #{self.case}")

    def after(self, info: DockerExecInfo):
        coverage = info.worktree.host / CoverageCommand.coverage_output
        name = f"{coverage.parent.name}-{self.case:04}.json"
        if not coverage.exists():
            message.warning(f"Failed to generate coverage data. {name} is not created")
            return
        # TODO: add option to control where to place json files.
        coverage = coverage.rename(f"{getcwd()}/{name}")
        message.info2(f"{name} is created at {str(coverage)}")


class CoverageCommand(TestCommandMixin, DockerCommand):
    """
    Run test and generate coverage data.
    """

    coverage_output = "coverage.json"
    default_options = ["--print-summary", "--delete", "--json", coverage_output]

    def __init__(self):
        super().__init__(instance=CoverageCommandLine)
        self.parser.usage = "d++ build --project=[project_name] --no=[number] --case=[index] [checkout directory]"

    def run(self, argv: List[str]) -> DockerExecInfo:
        args = self.parser.parse_args(argv)
        self._metadata = args.metadata
        self._worktree = args.worktree
        return self.generate(argv, coverage=True)

    def each_command(self, commands: List[str]) -> List[str]:
        exclude = " ".join(
            [f"--gcov-exclude {dir}" for dir in self._metadata.common.exclude]
        )
        commands.append(
            f"gcovr {' '.join(self.default_options)} {exclude} --root {self._metadata.common.root}"
        )
        return commands

    def setup(self, info: DockerExecInfo):
        message.info(f"Generating coverage data for {info.metadata.name}")

    def teardown(self, info: DockerExecInfo):
        message.info(f"Finished {info.metadata.name}")

    @property
    def help(self) -> str:
        return "Run test and generate coverage information about it"
