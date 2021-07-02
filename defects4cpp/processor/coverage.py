from os import getcwd
from pathlib import Path
from typing import List, Optional

import message
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import DockerCommand, DockerCommandArguments
from taxonomy import MetaData


class CoverageCommand(DockerCommand):
    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.usage = (
            "d++ build --project=[project_name] --no=[number] [checkout directory]"
        )
        self._coverage_name: Optional[str] = None
        self._volume: Optional[str] = None

    def run(self, argv: List[str]) -> DockerCommandArguments:
        args = self.parser.parse_args(argv)
        metadata: MetaData = args.metadata
        prefix: str = f"{'buggy' if args.buggy else 'fixed'}#{args.index}"
        self._coverage_name = f"coverage-{prefix}.json"
        self._volume = f"{args.workspace}/{metadata.name}/{prefix}"
        commands = [f"gcovr --branches --json {self._coverage_name}"]

        message.info(f"Generating coverage data for {metadata.name} {prefix}")
        return DockerCommandArguments(metadata.dockerfile, self._volume, commands)

    def done(self):
        assert self._coverage_name and self._volume
        coverage = Path(self._volume) / self._coverage_name
        coverage = coverage.rename(f"{getcwd()}/{self._coverage_name}")

        message.info(f"{self._coverage_name} is created at {str(coverage)}")

    @property
    def help(self) -> str:
        return "Coverage build local with a build tool from docker"
