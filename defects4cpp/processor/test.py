from typing import List

import message
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import DockerCommand, DockerCommandArguments
from taxonomy import MetaData


class TestCommand(DockerCommand):
    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.usage = (
            "d++ test --project=[project_name] --no=[number] [checkout directory]"
        )

    def run(self, argv: List[str]) -> DockerCommandArguments:
        args = self.parser.parse_args(argv)
        metadata: MetaData = args.metadata
        commands = [*metadata.common.test_cov_command]
        volume = f"{args.workspace}/{metadata.name}/{'buggy' if args.buggy else 'fixed'}#{args.index}"

        message.info(f"Running {metadata.name} test")
        return DockerCommandArguments(metadata.dockerfile, volume, commands)

    def done(self):
        pass

    @property
    def help(self) -> str:
        return "Do test without coverage"
