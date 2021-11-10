import argparse
import json
from os import environ
from pathlib import Path
from typing import Any, Dict, Optional, cast

import pytest

from defects4cpp.processor import BuildCommand, CheckoutCommand
from defects4cpp.processor.core import Command, Worktree, write_config
from defects4cpp.taxonomy import MetaData, Taxonomy


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


def _create_processor(
    name: str,
    workspace: Path,
    meta_json: Dict,
    extra_args: Dict,
    cmd: "Command",
) -> "Command":
    with open(workspace / "meta.json", "w+") as fp:
        json.dump(meta_json, fp)
    with open(workspace / "__init__.py", "w+") as fp:
        pass

    # Create a dummy taxonomy temporarily used for testing.
    t = Taxonomy()
    symlink = Path(t.base) / workspace.name
    symlink.symlink_to(workspace, target_is_directory=True)

    cmd.parser = argparse.ArgumentParser()
    worktree = Worktree(name, 1, extra_args["buggy"], str(workspace))
    if isinstance(cmd, BuildCommand):
        worktree.host.mkdir(parents=True, exist_ok=True)
        write_config(worktree)
    cmd.parser.set_defaults(
        path=str(worktree.host),
        metadata=MetaData(name=name, path=str(workspace)),
        worktree=worktree,
        index=1,
        **extra_args
    )

    return cmd


def _cleanup_create_processor(workspace: Path):
    t = Taxonomy()
    symlink = Path(t.base) / workspace.name
    if symlink.exists() and symlink.is_symlink():
        symlink.unlink()


@pytest.fixture
def create_checkout(tmp_path: Path, request):
    workspace = tmp_path / request.node.name
    workspace.mkdir(parents=True)

    def checkout(
        meta_json: Dict, extra_args: Optional[Dict] = None
    ) -> "CheckoutCommand":
        cmd = CheckoutCommand()
        extra_args = {} if extra_args is None else extra_args
        extra_args.setdefault("buggy", False)
        return cast(
            CheckoutCommand,
            _create_processor(request.node.name, workspace, meta_json, extra_args, cmd),
        )

    yield checkout

    _cleanup_create_processor(workspace)


@pytest.fixture
def create_build(tmp_path: Path, request):
    workspace = tmp_path / request.node.name
    workspace.mkdir(parents=True)

    def build(meta_json: Dict, extra_args: Optional[Dict] = None) -> "BuildCommand":
        cmd = BuildCommand()
        extra_args = {} if extra_args is None else extra_args
        extra_args.setdefault("buggy", False)
        extra_args.setdefault("verbose", False)
        return cast(
            BuildCommand,
            _create_processor(request.node.name, workspace, meta_json, extra_args, cmd),
        )

    yield build

    _cleanup_create_processor(workspace)


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
