import argparse
import json
from os import environ
from pathlib import Path
from textwrap import dedent
from typing import Any, Dict, Optional, cast

import pytest

from bugscpp.command import BuildCommand, CheckoutCommand
from bugscpp.config import config
from bugscpp.processor.core.command import Command
from bugscpp.processor.core.data import Project, Worktree
from bugscpp.taxonomy import MetaData, Taxonomy


def pytest_addoption(parser):
    parser.addoption(
        "--skip-slow",
        action="store_true",
        default=False,
        help="skip long tests",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--skip-slow"):
        skip_long = pytest.mark.skip(reason="need --skip-slow option to run")
        for item in items:
            if "slow" in item.keywords:
                item.add_marker(skip_long)


@pytest.fixture(autouse=True)
def gitenv():
    environ["GIT_COMMITTER_NAME"] = "bugscpp"
    environ["GIT_COMMITTER_EMAIL"] = "bugscpp@email.com"
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
    with open(workspace / "__init__.py", "w+"):
        pass

    # Create a dummy taxonomy temporarily used for testing.
    t = Taxonomy()
    symlink = Path(t.base) / workspace.name
    symlink.symlink_to(workspace, target_is_directory=True)

    cmd.parser = argparse.ArgumentParser()
    worktree = Worktree(name, 1, extra_args["buggy"], str(workspace))
    metadata = MetaData(name=name, path=str(workspace))

    if isinstance(cmd, BuildCommand):
        worktree.host.mkdir(parents=True, exist_ok=True)
        Project.write_config(worktree)
        with open(metadata.dockerfile, "w+") as fp:
            fp.write(
                dedent(
                    """FROM ubuntu:20.04
                RUN useradd --home-dir /home/workspace --shell /bin/bash defects4cpp
                USER defects4cpp
                ENV USER defects4cpp
                WORKDIR /home/workspace"""
                )
            )

    cmd.parser.set_defaults(
        path=str(worktree.host),
        metadata=metadata,
        metadata_base=t.base,
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
        extra_args.setdefault("env", None)

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
        extra_args.setdefault("coverage", False)
        extra_args.setdefault("verbose", False)
        extra_args.setdefault("env", None)
        extra_args.setdefault("export", None)
        extra_args.setdefault("rebuild", False)
        extra_args.setdefault("jobs", 1)

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
            "build": {"commands": [{"type": "docker", "lines": []}]},
            "build-coverage": {"commands": [{"type": "docker", "lines": []}]},
            "test-type": "automake",
            "test": {"commands": [{"type": "docker", "lines": []}]},
            "test-coverage": {"commands": [{"type": "docker", "lines": []}]},
            "gcov": {"exclude": [], "commands": [{"type": "docker", "lines": []}]},
        },
        "defects": [
            {
                "id": 1,
                "hash": "1",
                "num_cases": 1,
                "case": [1],
                "tags": [],
                "description": "test",
            },
        ],
    }


@pytest.fixture
def keep_config():
    orig = {k: getattr(config, k) for k in dir(config) if not k.startswith("__")}
    yield
    for k, v in orig.items():
        setattr(config, k, v)


@pytest.fixture
def resource_dir() -> Path:
    resource = Path(__file__).parent / "resource"
    assert resource.exists()
    return resource
