from pathlib import Path
from typing import List

import git
import message
from processor.core.argparser import create_taxonomy_parser
from processor.core.command import Command


class CheckoutCommand(Command):
    def __init__(self):
        super().__init__()
        self.parser = create_taxonomy_parser()
        self.parser.usage = "d++ checkout --project=[project_name] --no=[number]"

    def __call__(self, argv: List[str]):
        args = self.parser.parse_args(argv)
        metadata = args.metadata
        # TODO: share this method
        repo_path: Path = Path(f"{args.workspace}/{metadata.name}/.repo")
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

        checkout_dir = (
            repo_path.parent / f"{'buggy' if args.buggy else 'fixed'}#{args.index}"
        )
        if not checkout_dir.exists():
            try:
                # Pass '-f' in case worktree directory could be registered but removed.
                output = repo.git.worktree("add", "-f", str(checkout_dir), defect.hash)
            except git.GitCommandError:
                pass

            if args.buggy:
                buggy_repo = git.Repo(str(checkout_dir))
                buggy_repo.git.am(defect.patch)
        message.info(f"{metadata.name}: {defect.hash}")

    @property
    def group(self) -> str:
        return "v1"

    @property
    def help(self) -> str:
        return "Get a specific defect snapshot"
