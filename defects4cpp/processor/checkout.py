from os.path import exists
from pathlib import Path
from typing import List, Optional, Tuple

import git
from processor.core.argparser import TaxonomyArguments, TaxonomyParser
from processor.core.command import Command


class CheckoutCommandParser(TaxonomyParser):
    def __init__(self):
        super().__init__()
        self.parser.usage = "d++ checkout --project=[project_name] --no=[number]"


class CheckoutCommand(Command):
    parser = CheckoutCommandParser()

    def __init__(self):
        pass

    def __call__(self, argv: List[str]):
        taxonomy = self.parser(argv)
        metadata = taxonomy.metadata
        root = f"{taxonomy.root}/{metadata.name}"
        defect = metadata.defects[taxonomy.index]

        try:
            repo = git.Repo(root)
        except git.NoSuchPathError:
            repo = git.Repo.clone_from(metadata.info.url, root)

        checkout_dir = (
            Path(root).parent
            / f"{'buggy' if taxonomy.buggy else 'fixed'}#{taxonomy.index}"
        )
        if not exists(checkout_dir):
            try:
                # Pass '-f' in case worktree directory could be registered but removed.
                message = repo.git.worktree("add", "-f", checkout_dir, defect.hash)
                print(message)
            except git.GitCommandError:
                pass

            if taxonomy.buggy:
                buggy_repo = git.Repo(checkout_dir)
                buggy_repo.git.am(defect.patch)

    @property
    def group(self) -> str:
        return "v1"

    @property
    def help(self) -> str:
        return "Get a specific defect snapshot"
