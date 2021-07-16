from typing import List

import message
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import DockerCommand, DockerCommandLine, DockerExecInfo
from taxonomy import MetaData


class BuildCommandLine(DockerCommandLine):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def before(self, info: DockerExecInfo):
        pass

    def after(self, info: DockerExecInfo):
        pass


class BuildCommand(DockerCommand):
    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.add_argument(
            "--coverage",
            dest="coverage",
            help="build with gcov flags",
            action="store_true",
        )
        self.parser.usage = "d++ build --project=[project_name] --no=[number] [--coverage] [checkout directory]"

    def run(self, argv: List[str]) -> DockerExecInfo:
        args = self.parser.parse_args(argv)
        metadata: MetaData = args.metadata
        commands = (
            [BuildCommandLine(metadata.common.build_coverage_command)]
            if args.coverage
            else [BuildCommandLine(metadata.common.build_command)]
        )
        stream = False if args.quiet else True

        return DockerExecInfo(metadata, args.worktree, commands, stream)

    def setup(self, info: DockerExecInfo):
        message.info(f"Building {info.metadata.name}")

    def teardown(self, info: DockerExecInfo):
        pass

    @property
    def help(self) -> str:
        return "Build local with a build tool from docker"
