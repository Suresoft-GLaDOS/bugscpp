import argparse
import json
import sys
from os import environ
from os.path import abspath, dirname, join
from pathlib import Path
from typing import Any, Dict

import pytest
from processor.core import Worktree

import defects4cpp.processor
import defects4cpp.taxonomy

root_dir = dirname(dirname(abspath(__file__)))
sys.path.extend([root_dir, join(root_dir, "defects4cpp")])


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
def create_checkout(tmp_path: Path, request):
    workspace = tmp_path / request.node.name
    workspace.mkdir(parents=True)

    def checkout(meta_json: Dict, buggy: bool) -> defects4cpp.processor.CheckoutCommand:
        with open(workspace / "meta.json", "w+") as fp:
            json.dump(meta_json, fp)

        cmd = defects4cpp.processor.CheckoutCommand()
        cmd.parser = argparse.ArgumentParser()
        cmd.parser.set_defaults(
            metadata=defects4cpp.taxonomy.MetaData(
                name=request.node.name, path=workspace
            ),
            worktree=Worktree(request.node.name, 1, buggy, str(workspace)),
            buggy=buggy,
            index=1,
        )
        return cmd

    return checkout


@pytest.fixture
def meta_json() -> Dict[str, Any]:
    return {
        "info": {"url": "test-url", "short-desc": "", "vcs": "git"},
        "common": {
            "build": {"command": {"type": "docker", "lines": []}},
            "build-coverage": {"command": {"type": "docker", "lines": []}},
            "test-type": "automake",
            "test": {"command": {"type": "docker", "lines": []}},
            "test-coverage": {"command": {"type": "docker", "lines": []}},
            "gcov": {"exclude": [], "command": {"type": "docker", "lines": []}},
        },
        "defects": [
            {
                "hash": "1",
                "num_cases": 1,
                "case": [1],
                "description": "test",
            },
        ],
    }


@pytest.fixture
def resource_dir() -> Path:
    resource = Path(__file__).parent / "resource"
    assert resource.exists()
    return resource
