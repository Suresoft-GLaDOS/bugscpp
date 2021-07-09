from typing import List

import message
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import DockerCommand, DockerCommandArguments
from taxonomy import MetaData


class BuildCommand(DockerCommand):
    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.usage = (
            "d++ build --project=[project_name] --no=[number] [checkout directory]"
        )

    def run(self, argv: List[str]) -> DockerCommandArguments:
        args = self.parser.parse_args(argv)
        metadata: MetaData = args.metadata
        commands = [*metadata.common.build_command]

        message.info(f"Building {metadata.name}")
        return DockerCommandArguments(metadata.dockerfile, args.worktree, commands)

    def setup(self):
        pass

    def teardown(self):
        pass

    @property
    def help(self) -> str:
        return "Build local with a build tool from docker"
