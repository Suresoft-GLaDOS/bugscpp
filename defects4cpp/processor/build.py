from typing import Generator, List, Optional

import message
import taxonomy
from processor.core.argparser import create_common_project_parser, read_config
from processor.core.command import DockerCommand, DockerCommandScript, DockerCommandScriptGenerator
from processor.core.docker import Worktree


class BuildCommandScript(DockerCommandScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def before(self):
        pass

    def output(self, linenr: Optional[int], exit_code: int, stream: str):
        pass

    def after(self):
        pass


class BuildCommandScriptGenerator(DockerCommandScriptGenerator):
    def __init__(
        self,
        command: taxonomy.Command,
        metadata: taxonomy.MetaData,
        worktree: Worktree,
        stream: bool,
    ):
        super().__init__(metadata, worktree, stream)
        self.command = command

    def create(self) -> Generator[BuildCommandScript, None, None]:
        yield BuildCommandScript(self.command.type, self.command.lines)


class BuildCommand(DockerCommand):
    """
    Run build command either with or without coverage.
    """

    def __init__(self):
        super().__init__()
        self.parser = create_common_project_parser()
        self.parser.usage = "d++ build --project=[project_name] --no=[number] [--coverage] [checkout directory]"

    def create_script_generator(self, argv: List[str]) -> DockerCommandScriptGenerator:
        args = self.parser.parse_args(argv)

        metadata, worktree = read_config(args.path)
        command = (
            metadata.common.build_coverage_command
            if args.coverage
            else metadata.common.build_command
        )
        stream = True if args.verbose else False

        return BuildCommandScriptGenerator(command, metadata, worktree, stream)

    def setup(self, generator: DockerCommandScriptGenerator):
        message.info(f"Building {generator.metadata.name}")

    def teardown(self, generator: DockerCommandScriptGenerator):
        pass

    @property
    def help(self) -> str:
        return "Build local with a build tool from docker"
