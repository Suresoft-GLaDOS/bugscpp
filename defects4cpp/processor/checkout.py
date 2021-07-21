from pathlib import Path
from typing import List

import git
import message
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import Command


class CheckoutCommand(Command):
    """
    Checkout command which handles VCS commands based on taxonomy information.
    """

    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.usage = "d++ checkout --project=[project_name] --no=[number]"

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

            # Apply buggy patch
            checkout_repo = git.Repo(checkout_dir)
            if args.buggy:
                checkout_repo.git.am(defect.buggy_patch)
            # Apply split patch
            checkout_repo.git.am(defect.split_patch)

        message.info(f"{metadata.name}: {defect.hash}")

    @property
    def group(self) -> str:
        return "v1"

    @property
    def help(self) -> str:
        return "Get a specific defect snapshot"
