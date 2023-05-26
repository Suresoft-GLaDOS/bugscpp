import itertools
import json
from dataclasses import asdict

import pytest
from errors import (DppArgparseConfigCorruptedError, DppArgparseFileNotFoundError, DppArgparseInvalidConfigError,
                    DppArgparseNotProjectDirectory)

from bugscpp.config import config
from bugscpp.errors import DppArgparseInvalidEnvironment
from bugscpp.processor.core.argparser import (create_common_parser, create_common_project_parser,
                                              create_common_vcs_parser)
from bugscpp.processor.core.data import Project, Worktree
from bugscpp.taxonomy import Taxonomy

CONFIG_NAME = ".defects4cpp.json"


def test_read_config_not_exist(tmp_path):
    with pytest.raises(DppArgparseFileNotFoundError):
        Project.read_config(str(tmp_path / "foo.json"))


def test_read_config_invalid_json(tmp_path):
    dummy = tmp_path / CONFIG_NAME
    with open(dummy, "w+") as fp:
        fp.write("hello, world!")

    with pytest.raises(DppArgparseInvalidConfigError):
        Project.read_config(tmp_path)


def test_read_config_corrupted_json(tmp_path):
    dummy = tmp_path / CONFIG_NAME
    with open(dummy, "w+") as fp:
        obj = {"foo": 1}
        json.dump(obj, fp)

    with pytest.raises(DppArgparseConfigCorruptedError):
        Project.read_config(tmp_path)


def test_read_config(tmp_path):
    dummy = tmp_path / CONFIG_NAME
    with open(dummy, "w+") as fp:
        obj = {
            "project_name": "yara",
            "index": 1,
            "buggy": False,
            "workspace": str(tmp_path),
        }
        json.dump(obj, fp)

    metadata, worktree = Project.read_config(tmp_path)

    assert metadata.name == obj["project_name"]
    assert worktree.project_name == obj["project_name"]
    assert worktree.index == obj["index"]
    assert worktree.buggy == obj["buggy"]
    assert worktree.workspace == obj["workspace"]


def test_write_config(tmp_path):
    worktree = Worktree("yara", 1, True, str(tmp_path / "imaginary_path"))

    with pytest.raises(DppArgparseFileNotFoundError):
        Project.write_config(worktree)

    p = tmp_path / "yara" / "buggy-1"
    p.mkdir(parents=True)

    worktree = Worktree("yara", 1, True, str(tmp_path))
    Project.write_config(worktree)

    with open(p / CONFIG_NAME, "r") as fp:
        config = json.load(fp)

    assert asdict(worktree) == config


def test_project_parser_invalid_project_should_throw(tmp_path):
    parser = create_common_project_parser()

    with pytest.raises(DppArgparseNotProjectDirectory):
        parser.parse_args(f"{tmp_path} --coverage".split())


def test_project_parser_should_read_config_json(tmp_path):
    parser = create_common_project_parser()
    project_name = "yara"

    with open(tmp_path / CONFIG_NAME, "w+") as fp:
        obj = {
            "project_name": project_name,
            "index": 1,
            "buggy": False,
            "workspace": str(tmp_path),
        }
        json.dump(obj, fp)

    args = parser.parse_args(f"{tmp_path} --coverage".split())

    assert hasattr(args, "metadata")
    assert args.metadata.name == project_name
    assert hasattr(args, "worktree")
    assert not args.worktree.buggy
    assert args.worktree.index == 1
    assert args.path == str(tmp_path)


def test_vcs_parser_invalid_project_should_throw():
    parser = create_common_vcs_parser()

    with pytest.raises(SystemExit):
        parser.parse_args("foobar 1 --buggy".split())


@pytest.mark.parametrize("cmd_line", ["yara 1 --buggy", "yara --buggy 1"])
def test_vcs_parser_unordered_arguments_should_be_handled(cmd_line):
    parser = create_common_vcs_parser()

    args = parser.parse_args(cmd_line.split())
    metadata = args.metadata
    worktree = args.worktree

    assert metadata.name == "yara"
    assert worktree.index == 1
    assert worktree.buggy


def test_vcs_parser_unordered_arguments_should_be_handled_with_target_option():
    parser = create_common_vcs_parser()
    arguments = ["1", "--buggy", "--target=/home/test"]

    for argument in itertools.permutations(arguments):
        args = parser.parse_args(["yara", *argument])
        metadata = args.metadata
        worktree = args.worktree

        assert metadata.name == "yara"
        assert worktree.index == 1
        assert worktree.buggy
        assert worktree.workspace == "/home/test"


def test_common_project_parser_env_option(dummy_config, request):
    p = dummy_config(request.node.name)
    parser = create_common_project_parser()
    arguments = [
        str(p),
        "--env=MY_ENV1=1",
        "--env='MY_ENV2=2'",
        '--env="MY_ENV3=3"',
        "--env=MY_ENV4=",
    ]
    args = parser.parse_args(arguments)
    assert len(args.env) == 4

    arguments = [
        str(p),
        "--env=MY_ENV4=",
    ]
    args = parser.parse_args(arguments)
    assert len(args.env) == 1

    arguments = [
        str(p),
        "--env=MY_ENV4",
    ]
    with pytest.raises(DppArgparseInvalidEnvironment):
        parser.parse_args(arguments)

    arguments = [
        str(p),
        "--env==foo",
    ]
    with pytest.raises(DppArgparseInvalidEnvironment):
        parser.parse_args(arguments)


def test_common_command_parser_settings_option(keep_config):
    parser = create_common_parser()
    arguments = [
        "--compilation_db_tool=foo",
    ]
    parser.parse_args(arguments)

    assert config.DPP_COMPILATION_DB_TOOL == "foo"
    assert config.DPP_CMAKE_COMPILATION_DB_TOOL == "foo"

    t = Taxonomy()
    make_project = t["yara"]
    assert any(
        "foo" in line for line in make_project.common_capture.build_command[0].lines
    )

    cmake_project = t["cppcheck"]
    assert any(
        "foo" in line for line in cmake_project.common_capture.build_command[0].lines
    )
