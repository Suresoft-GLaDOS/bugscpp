import json
import sys
from os import environ
from os.path import abspath, dirname, join
from pathlib import Path

import pytest

root_dir = dirname(dirname(abspath(__file__)))
sys.path.extend([root_dir, join(root_dir, "defects4cpp")])


@pytest.fixture
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
