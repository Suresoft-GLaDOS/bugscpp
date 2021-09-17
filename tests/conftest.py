import json
import re
import sys
from dataclasses import dataclass
from os import environ
from os.path import abspath, dirname, join
from pathlib import Path
from typing import Callable

import pytest

root_dir = dirname(dirname(abspath(__file__)))
sys.path.extend([root_dir, join(root_dir, "defects4cpp")])


@dataclass
class TestDirectory:
    project: str
    checkout_dir: Path
    fixed_target_dir: Path
    fixed_output_dir: Path
    buggy_target_dir: Path
    buggy_output_dir: Path
    __test__ = False


@pytest.fixture(autouse=True)
def gitenv():
    environ["GIT_COMMITTER_NAME"] = "defects4cpp"
    environ["GIT_COMMITTER_EMAIL"] = "defects4cpp@email.com"
    yield
    del environ["GIT_COMMITTER_NAME"]
    del environ["GIT_COMMITTER_EMAIL"]


@pytest.fixture
def dummy_config(tmp_path: Path):
    def create_dummy_config(name: str) -> Path:
        p = tmp_path / name
        p.mkdir()
        dummy = p / ".defects4cpp.json"
        with open(dummy, "w+") as fp:
            obj = {
                "project_name": "yara",
                "index": 1,
                "buggy": False,
                "workspace": str(p),
            }
            json.dump(obj, fp)
        return p

    return create_dummy_config


@pytest.fixture
def defect_path(tmp_path: Path, request) -> Callable[[int, int], TestDirectory]:
    def create_defect_path(index: int, case: int) -> TestDirectory:
        # test_PROJECT_NAME
        regex = re.compile(r"test_(.*)\[.*\]")
        project = regex.match(request.node.name).groups()[0]

        d = tmp_path / request.node.name
        d.mkdir()
        return TestDirectory(
            project,
            d,
            fixed_target_dir=(d / project / f"fixed#{index}"),
            fixed_output_dir=(d / f"{project}-fixed#{index}-{case}"),
            buggy_target_dir=(d / project / f"buggy#{index}"),
            buggy_output_dir=(d / f"{project}-buggy#{index}-{case}"),
        )

    return create_defect_path
