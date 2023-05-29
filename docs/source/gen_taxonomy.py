#!/usr/bin/env python3
import json
import sys
from os.path import realpath
from pathlib import Path

project_root = Path(realpath(__file__)).parent.parent.parent
assert project_root / "pyproject.toml", f"{project_root} is not a project root"
taxonomy_path = Path("bugscpp/taxonomy")

table = """.. _taxonomy:

A List of Defect Taxonomy
=========================

.. list-table:: Defect Taxonomy
   :header-rows: 1

   * - Project
     - bug_ID
     - files
     - linesAdd
     - linesDel
     - methods
     - sizeInLines
"""

rows = []
for entry in (project_root / taxonomy_path).iterdir():
    if not entry.is_dir() or entry.name.startswith("__"):
        continue
    with open(entry / "meta.json") as fp:
        meta = json.load(fp)
        num_of_defects = len(meta["defects"])
    for index in range(num_of_defects):
        patch_name = str(index + 1).zfill(4) + "-buggy.patch"
        with open(entry / "patch" / patch_name) as buggy:
            buggy_lines = buggy.readlines()
            bug_id = index + 1
            files_changed = 0
            lines_add = 0
            lines_del = 0
            methods = 0
            for line in buggy_lines:
                lines = line.split()
                if len(lines) == 0:
                    continue

                # check the number of files , added_lines , deleted_lines
                if len(lines) > 2 and lines[2] == "changed,":
                    files_changed = lines[0]
                    # buggy patch with insertion and deletion
                    if len(line.split()) == 7:
                        lines_add = int(lines[3])
                        lines_del = int(lines[5])
                    # buggy patch only with deletion
                    elif line[-3] == "-":
                        lines_del = int(lines[3])
                    # buggy patch only with insertion
                    elif line[-3] == "+":
                        lines_add = int(lines[3])

                # check methods in patch
                if lines[0] == "@@":
                    methods += 1

        rows.append(f"   * - {entry.name}\n")
        rows.append(f"     - {bug_id}\n")
        rows.append(f"     - {files_changed}\n")
        rows.append(f"     - {lines_add}\n")
        rows.append(f"     - {lines_del}\n")
        rows.append(f"     - {methods}\n")
        rows.append(f"     - {lines_add + lines_del}\n")

with open(project_root / "docs/source/taxonomy.rst", "w+") as fp:
    fp.write(f"{table}{''.join(rows)}")
