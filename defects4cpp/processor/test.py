import argparse
from pathlib import Path
from typing import List, Optional

import message
import taxonomy
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import DockerCommand, DockerCommandArguments
from processor.core.docker import Worktree


class ValidateCase(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        # TODO:
        # t = Taxonomy()
        # if values not in t.keys():
        #     raise KeyError(f"Taxonomy '{values}' does not exist")
        setattr(namespace, self.dest, values)


class TestCommand(DockerCommand):
    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.usage = "d++ test --project=[project_name] --no=[number] --case=[number] [checkout directory]"
        self.parser.add_argument(
            "-c",
            "--case",
            help="Index of test cases to run",
            type=int,
            dest="case",
            action=ValidateCase,
        )

    def run(self, argv: List[str]) -> DockerCommandArguments:
        args = self.parser.parse_args(argv)
        metadata: taxonomy.MetaData = args.metadata
        index = args.index
        commands = [
            self._select_index(metadata.defects[index - 1], index),
            *metadata.common.test_command,
        ]
        worktree = args.worktree

        # Clean remaining .gcda files if exist
        gcda = list(Path(worktree.host).rglob("*.gcda"))
        for g in gcda:
            g.unlink()

        message.info(f"Running {metadata.name} test")
        return DockerCommandArguments(metadata.dockerfile, worktree, commands)

    def _select_index(self, defect: taxonomy.Defect, index: int):
        """
        Returns command to run inside docker that modifies lua script return value which will be used to select which test case to run.

        Assume that "split.patch" newly creates "defects4cpp.lua" file.
        Read "split.patch" and get line containing "create mode ... defects4cpp.lua"
        This should retrieve the path to "defects4cpp.lua" relative to the project directory.
        """
        with open(defect.split_patch) as fp:
            lines = [line for line in fp if "create mode" in line]

        lua_path: Optional[str] = None
        for line in lines:
            if "defects4cpp.lua" in line:
                # "create mode number filename"[-1] == filename
                lua_path = line.split()[-1]
                break
        if not lua_path:
            raise AssertionError(f"could not get lua_path in {defect.split_patch}")
        return f"echo 'return {index}' > {lua_path}"

    def setup(self):
        pass

    def teardown(self):
        pass

    @property
    def help(self) -> str:
        return "Do test without coverage"
