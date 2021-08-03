#!/usr/bin/python3
import sys
from os import getcwd
from pathlib import Path
from typing import Dict, List

import git

KEYWORDS = ("fix", "bug")
DIRECTORY = ("src", "test")
EXTENSION = (".cpp", ".c")


def check_message(commit_msg: str):
    # Find keywords in commit message.
    return any(k in commit_msg.lower() for k in KEYWORDS)


def check_files(commit_files: Dict[str, Dict[str, int]]):
    files = commit_files.keys()
    # Consider modified files inside DIRECTORY only.
    for d in DIRECTORY:
        if not any(file.startswith(d) for file in files):
            return False

    # Extensions should be any of EXTENSIONS.
    if not any(Path(file).suffix in EXTENSION for file in files):
        return False

    # If the number of files are too big, get rid of it from candidates.
    return len(files) < 8


def iter_pair_commits(repo: git.Repo):
    it = repo.iter_commits("master")
    try:
        current_commit = next(it)
    except StopIteration:
        print("Project is too small")
        sys.exit(0)

    for next_commit in it:
        yield current_commit, next_commit
        current_commit = next_commit


def main(argv: List[str]):
    path = Path(argv[0])
    repo = git.Repo(str(path))

    for current_commit, next_commit in iter_pair_commits(repo):
        if not check_message(str(current_commit.message)):
            continue
        if not check_files(current_commit.stats.files):
            continue

        p = Path(getcwd()) / current_commit.hexsha
        p.mkdir(parents=True)
        with open(p / "commit-message", "w+", encoding='utf-8') as fp:
            fp.write(str(current_commit.message))
        with open(p / "diff.patch", "w+", encoding='utf-8') as patch_file:
            for patch in current_commit.diff(next_commit, create_patch=True):
                patch_file.write(patch.diff.decode("utf-8"))


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
