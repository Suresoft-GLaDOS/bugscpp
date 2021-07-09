from os import getcwd
from pathlib import Path
from typing import List, Optional

import message
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import DockerCommand, DockerCommandArguments
from processor.core.docker import Worktree
from taxonomy import MetaData


class CoverageCommand(DockerCommand):
    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.usage = (
            "d++ build --project=[project_name] --no=[number] [checkout directory]"
        )

    def run(self, argv: List[str]) -> DockerCommandArguments:
        args = self.parser.parse_args(argv)
        metadata: MetaData = args.metadata
        prefix: str = f"{'buggy' if args.buggy else 'fixed'}#{args.index}"
        self._coverage_name: str = f"coverage-{prefix}.json"
        self._worktree: Worktree = args.worktree
        exclude_options = (
            [f"--gcov-exclude {dir}" for dir in metadata.common.exclude]
            if metadata.common.exclude
            else ""
        )
        commands = [
            f"gcovr -r {metadata.common.root} {' '.join(exclude_options)} --branches --json {self._coverage_name}"
        ]

        message.info(f"Generating coverage data for {metadata.name} {prefix}")
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
