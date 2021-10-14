"""
Checkout command.

Clone a repository into the given directory on the host machine.
"""
from pathlib import Path
from typing import List

import git
import message
from processor.core import Command, create_common_vcs_parser, write_config


class CheckoutCommand(Command):
    """
    Checkout command which handles VCS commands based on taxonomy information.
    """

    def __init__(self):
        super().__init__()
        # TODO: write argparse description in detail
        self.parser = create_common_vcs_parser()
        self.parser.usage = "d++ checkout PROJECT INDEX [-b|--buggy] [-t|--target]"

    def __call__(self, argv: List[str]):
        """
        Clone a repository into the given directory or checkout to a specific commit on the host machine.
        It does not perform action inside a container unlike the other commands.
        It utilizes git-worktree rather than cleaning up the current directory and checking out.
        It not only makes hoping around commits more quickly, but also reduces overhead of writing and deleting files.

        Parameters
        ----------
        argv : List[str]
            Command line argument vector.

        Returns
        -------
        None
        """
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
            # Apply additional patch if it exists.
            for patch in [defect.split_patch, defect.fix_patch]:
                if patch:
                    checkout_repo.git.am(patch)

        # Write .defects4cpp.json in the directory.
        write_config(worktree)
        message.info(f"{metadata.name}: {defect.hash}")

    @property
    def group(self) -> str:
        return "v1"

    @property
    def help(self) -> str:
        return "Get a specific defect snapshot"
