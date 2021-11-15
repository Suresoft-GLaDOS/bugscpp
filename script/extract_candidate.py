#!/usr/bin/python3
import sys
from datetime import datetime
from os import getcwd
from pathlib import Path
from typing import Dict, Generator, List, Tuple

import git

KEYWORDS = ("fix", "bug")
DIRECTORY = ("src", "tests")
EXTENSION = (".cpp", ".c")
AGE = 2
DIFF_CONTENTS = 100
NUM_FILE = 8


def check_message(commit_msg: str):
    # Find keywords in commit message.
    return any(k in commit_msg.lower() for k in KEYWORDS)


def check_files(commit_files: Dict[str, Dict[str, int]]):
    # If the number of files are too big, get rid of it from candidates.
    if len(commit_files) > NUM_FILE:
        return False

    # Consider modified files inside DIRECTORY only.
    for d in DIRECTORY:
        if not any(file.startswith(d) for file in commit_files):
            return False

    # Extensions should be any of EXTENSIONS.
    if not any(Path(file).suffix in EXTENSION for file in commit_files):
        return False

    # Check the number of inserted lines and deleted lines.
    inserted_lines = sum(
        commit_files[src]["insertions"]
        for src in (file for file in commit_files if Path(file).suffix in EXTENSION)
    )
    deleted_lines = sum(
        commit_files[src]["deletions"]
        for src in (file for file in commit_files if Path(file).suffix in EXTENSION)
    )
    return (inserted_lines + deleted_lines) < DIFF_CONTENTS


def iter_pair_commits(
    repo: git.Repo,
) -> Generator[Tuple[git.Commit, git.Commit], None, None]:
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

    now = datetime.now()
    time_threshold = 365 * AGE
    count = 0

    for index, (current_commit, next_commit) in enumerate(
        iter_pair_commits(repo), start=1
    ):
        if index % 100 == 0:
            print(f"Iterating {index} commits")

        # Consider commits in the last two years.
        commit_datetime = datetime.fromtimestamp(current_commit.committed_date)
        if (now - commit_datetime).days > time_threshold:
            print(
                f"Commits made more than {AGE} years ago are not considered. Stop iterating commits."
            )
            break

        if not check_message(str(current_commit.message)):
            continue
        if not check_files(current_commit.stats.files):
            continue

        p = Path(getcwd()) / current_commit.hexsha
        p.mkdir(parents=True)
        with open(p / "commit-message", "w+", encoding="utf-8") as fp:
            fp.write(str(current_commit.message))
        with open(p / "diff.patch", "w+", encoding="utf-8") as patch_file:
            for patch in next_commit.diff(current_commit, create_patch=True):
                patch_file.write(f"diff --git {patch.a_path} {patch.b_path}\n")
                patch_file.write(patch.diff.decode("utf-8", errors="ignore"))
                patch_file.write("\n")
        # Progress info
        count += 1
        print(f"Current # of candidate: {count}")


if __name__ == "__main__":
    main(sys.argv[1:])
