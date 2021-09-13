from os.path import exists
from pathlib import Path
from typing import List

import git
import message
from processor.core.argparser import create_common_vcs_parser, write_config
from processor.core.command import Command


class CheckoutCommand(Command):
    """
    Checkout command which handles VCS commands based on taxonomy information.
    """

    def __init__(self):
        super().__init__()
        self.parser = create_common_vcs_parser()
        self.parser.usage = "d++ checkout project index"

    def __call__(self, argv: List[str]):
        args = self.parser.parse_args(argv)
        metadata = args.metadata
        worktree = args.worktree
        repo_path: Path = worktree.base / ".repo"
        # args.index is 1 based.
        defect = metadata.defects[args.index - 1]

        try:
            repo = git.Repo(str(repo_path))
        except git.NoSuchPathError:
            if not repo_path.parent.exists():
                repo_path.parent.mkdir(parents=True, exist_ok=True)
            message.info(f"cloning a new repository from {metadata.info.url}")
            repo = git.Repo.clone_from(metadata.info.url, str(repo_path))
        else:
            pass

        if not worktree.host.exists():
            checkout_dir = str(worktree.host)
            try:
                # Pass '-f' in case worktree directory could be registered but removed.
                repo.git.worktree("add", "-f", checkout_dir, defect.hash)
            except git.GitCommandError:
                # TODO: hmm..
                pass

            checkout_repo = git.Repo(checkout_dir)
            # Invoke command manually, because it seems like GitPython has a bug with updating submodules.
            if checkout_repo.submodules:
                checkout_repo.git.execute(["git", "submodule", "update", "--init"])
            # Apply buggy patch
            if args.buggy:
                checkout_repo.git.am(defect.buggy_patch)
            # Apply split patch if it exists.
            if exists(defect.split_patch):
                checkout_repo.git.am(defect.split_patch)
            # Apply fix patch if it exists.
            if exists(defect.fix_patch):
                checkout_repo.git.am(defect.fix_patch)

        # Write .defects4cpp.json in the directory.
        write_config(worktree)
        message.info(f"{metadata.name}: {defect.hash}")

    @property
    def group(self) -> str:
        return "v1"

    @property
    def help(self) -> str:
        return "Get a specific defect snapshot"
