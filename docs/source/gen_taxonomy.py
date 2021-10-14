#!/usr/bin/env python3
import json
import sys
from os.path import realpath
from pathlib import Path

path = Path(realpath(__file__))
while True:
    path = path.parent
    if path.parent == path:
        sys.exit(1)
    if path.name == "defects4cpp":
        break
taxonomy_path = Path("defects4cpp/taxonomy")

table = """.. _taxonomy:

A List of Defect Taxonomy
=========================

.. list-table:: Defect Taxonomy
   :widths: 40 40
   :header-rows: 1

   * - Project
     - # of bugs
"""

rows = []
for entry in (path / taxonomy_path).iterdir():
    if not entry.is_dir() or entry.name.startswith("__"):
        continue
    with open(entry / "meta.json") as fp:
        meta = json.load(fp)
    rows.append(f"   * - {entry.name}\n")
    rows.append(f"     - {len(meta['defects'])}\n")

with open(path / "docs/source/taxonomy.rst", "w+") as fp:
    fp.write(f"{table}{''.join(rows)}")
