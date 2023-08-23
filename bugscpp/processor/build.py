"""
Build command.

Compile projects inside a container.
"""
import argparse
import os
import shutil
from pathlib import Path
from textwrap import dedent
from typing import TYPE_CHECKING, Generator, List, Optional

from errors import DppArgparseFileNotFoundError

if TYPE_CHECKING:
    from taxonomy import Command, MetaData

from message import message
from processor.core.argparser import create_common_project_parser
from processor.core.command import DockerCommand, DockerCommandScript, DockerCommandScriptGenerator
from processor.core.data import Worktree


class ValidateExportPath(argparse.Action):
    """
    Validator for export path argument.
    """

    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: Optional[Path],
        option_string=None,
    ):
        values = values or Path(os.getcwd())
        if not values.absolute().exists():
            raise DppArgparseFileNotFoundError(str(values))
        setattr(namespace, self.dest, values)


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
        command: List["Command"],
        metadata: "MetaData",
        worktree: Worktree,
        verbose: bool,
    ):
        super().__init__(metadata, worktree, verbose)
        self.command = command

    def create(self) -> Generator[BuildCommandScript, None, None]:
        return (
            BuildCommandScript(self.stream, cmd.type, cmd.lines) for cmd in self.command
        )


class BuildCommand(DockerCommand):
    def __init__(self):
        super().__init__(parser=create_common_project_parser())
        self._export_path: Optional[Path] = None
        # TODO: write argparse description in detail
        self.parser.add_argument(
            "-e",
            "--export",
            type=Path,
            dest="export",
            help="export build commands.",
            nargs="?",
            action=ValidateExportPath,
        )
        self.parser.add_argument(
            "-u",
            "--uid",
            type=Path,
            dest="uid",
            help="set uid of user defects4cpp",
            nargs="?",
        )
        self.parser.usage = (
            "bugcpp.py build PATH [-j|--jobs=JOBS] [--coverage] [-v|--verbose] [-u|--uid=UID_DPP_DOCKER_USER] "
            "[-e|--export[=EXPORT_PATH]]"
        )
        self.parser.description = dedent(
            """\
        Build project inside docker.
        """
        )

    def create_script_generator(
        self, args: argparse.Namespace
    ) -> DockerCommandScriptGenerator:
        metadata = args.metadata
        worktree = args.worktree

        self._export_path = args.export
        common = metadata.common_capture if self._export_path else metadata.common
        command = (
            common.build_coverage_command if args.coverage else common.build_command
        )
        return BuildCommandScriptGenerator(command, metadata, worktree, args.verbose)

    def setup(self, generator: DockerCommandScriptGenerator):
        message.info(__name__, f"'{generator.metadata.name}'")
        message.stdout_progress(f"[{generator.metadata.name}] start building")

    def teardown(self, generator: DockerCommandScriptGenerator):
        if self._export_path:
            message.info(__name__, f"export to '{str(self._export_path)}'")
            self._find_compile_commands_json(generator.worktree.host, self._export_path)

        message.info(__name__, "done")
        message.stdout_progress(f"[{generator.metadata.name}] done")

    @property
    def help(self) -> str:
        return "Build local with a build tool from docker"

    @staticmethod
    def _find_compile_commands_json(host: Path, dest: Path):
        build_dir = host / "build"
        if build_dir.exists():
            compile_commands = build_dir / "compile_commands.json"
        else:
            compile_commands = host / "compile_commands.json"

        if compile_commands.exists():
            shutil.copyfile(str(compile_commands), str(dest / "compile_commands.json"))
        else:
            message.warning(__name__, "compile_commands.json could not be found")
