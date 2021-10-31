"""
Build command.

Compile projects inside a container.
"""
from textwrap import dedent
from typing import Generator, List, Optional

import taxonomy
from message import message
from processor.core import (DockerCommand, DockerCommandScript, DockerCommandScriptGenerator, Worktree,
                            create_common_project_parser, read_config)


class BuildCommandScript(DockerCommandScript):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def before(self):
        pass

    def output(self, linenr: Optional[int], exit_code: Optional[int], stream: str):
        if not exit_code:
            return

        if exit_code != 0:
            message.warning(__name__, f"build command exit with {exit_code}")

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
    def __init__(self):
        super().__init__()
        # TODO: write argparse description in detail
        self.parser = create_common_project_parser()
        self.parser.usage = "d++ build PATH [--coverage] [-v|--verbose]"
        self.parser.description = dedent(
            """\
        Build project inside docker.
        """
        )

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
        message.info(__name__, f"'{generator.metadata.name}'")
        message.stdout_progress(f"[{generator.metadata.name}] start building")

    def teardown(self, generator: DockerCommandScriptGenerator):
        message.info(__name__, f"done")
        message.stdout_progress(f"[{generator.metadata.name}] done")

    @property
    def help(self) -> str:
        return "Build local with a build tool from docker"
