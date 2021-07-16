#!/usr/bin/python3
import os
import re
from typing import List


def main(argv: List[str]):
    patch = argv[0]
    if not os.path.exists(patch):
        print("No diff patch is passed")
        return

    with open(patch, "r") as fp:
        contents = fp.readlines()

    count: int = 1
    new_contents: List[str] = []
    for line in contents:
        if line.startswith("+"):
            if "case" in line:
                line = re.sub(
                    "(?P<switch>\\s*case\\s*)\\d*:\n", f"\\g<switch>{count}:\n", line
                )
                count += 1
        elif line.startswith("-"):
            if not line.startswith("--") and line != "-\n":
                print(f"Warning '{line[:-1]}'")
        elif line == "<<<<<<< HEAD":
            print(f"Error '{line[:-1]}'")
        new_contents.append(line)

    with open("./new_patch.patch", "w+") as fp:
        fp.writelines(new_contents)
    print(f"total: {count}")


if __name__ == "__main__":
    import sys

    main(sys.argv[1:])
