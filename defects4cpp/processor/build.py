"""
Build command.

Compile projects inside a container.
"""
from textwrap import dedent
from typing import TYPE_CHECKING, Generator, List, Optional

if TYPE_CHECKING:
    from taxonomy import Command, MetaData

from message import message
from processor.core import (
    DockerCommand,
    DockerCommandScript,
    DockerCommandScriptGenerator,
    Worktree,
    create_common_project_parser,
    read_config,
)


class BuildCommandScript(DockerCommandScript):
    def __init__(self, verbose: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._verbose = verbose

    def before(self):
        pass

    def step(self, linenr: int, line: str):
        if self._verbose:
            message.stdout_progress_detail(f"defects4cpp.build[{linenr}]: {line}")

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
        command: "Command",
        metadata: "MetaData",
        worktree: Worktree,
        verbose: bool,
    ):
        super().__init__(metadata, worktree, verbose)
        self.command = command

    def create(self) -> Generator[BuildCommandScript, None, None]:
        yield BuildCommandScript(self.stream, self.command.type, self.command.lines)


class BuildCommand(DockerCommand):
    def __init__(self):
        super().__init__()
        # TODO: write argparse description in detail
        self.parser = create_common_project_parser()
        self.parser.add_argument(
            "-e",
            "--export",
            dest="export",
            help="export build commands.",
            action="store_true",
        )
        self.parser.usage = "d++ build PATH [--coverage] [-v|--verbose] [-e|--export]"
        self.parser.description = dedent(
            """\
        Build project inside docker.
        """
        )

    def create_script_generator(self, argv: List[str]) -> DockerCommandScriptGenerator:
        args = self.parser.parse_args(argv)

        metadata, worktree = read_config(args.path)
        common = metadata.common_capture if args.export else metadata.common
        command = (
            common.build_coverage_command if args.coverage else common.build_command
        )
        return BuildCommandScriptGenerator(command, metadata, worktree, args.verbose)

    def setup(self, generator: DockerCommandScriptGenerator):
        message.info(__name__, f"'{generator.metadata.name}'")
        message.stdout_progress(f"[{generator.metadata.name}] start building")

    def teardown(self, generator: DockerCommandScriptGenerator):
        message.info(__name__, "done")
        message.stdout_progress(f"[{generator.metadata.name}] done")

    @property
    def help(self) -> str:
        return "Build local with a build tool from docker"
