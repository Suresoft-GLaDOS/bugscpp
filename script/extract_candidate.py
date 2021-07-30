#!/usr/bin/python3
import sys
from os import getcwd
from pathlib import Path
from typing import Dict, List

import git

KEY_WORDS = ("fix", "bug")
DIRECTORY = ("src", "test")


def check_message(commit_msg: str):
    return any(k in commit_msg.lower() for k in KEY_WORDS)


def check_files(commit_files: Dict[str, Dict[str, int]]):
    files = commit_files.keys()
    for d in DIRECTORY:
        if not any(file.startswith(d) for file in files):
            return False
    # If the number of files are too bit, get rid of it from candidates.
    return len(files) < 8


def main(argv: List[str]):
    path = Path(argv[0])
    repo = git.Repo(str(path))
    for commit in repo.iter_commits("master"):
        if not check_message(str(commit.message)):
            continue
        if not check_files(commit.stats.files):
            continue

        p = Path(getcwd()) / commit.hexsha
        p.mkdir(parents=True)
        with open(p / "commit-message", "w+") as fp:
            fp.write(str(commit.message))
        with open(p / "diff.patch", "w+") as patch_file:
            for patch in commit.diff(create_patch=True):
                patch_file.write(patch.diff.decode("utf-8"))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
