import itertools
import json
from dataclasses import asdict

import errors
import pytest
from processor.core.argparser import create_common_project_parser, create_common_vcs_parser, read_config, write_config
from processor.core.docker import Worktree

CONFIG_NAME = ".defects4cpp.json"


def test_read_config_not_exist(tmp_path):
    with pytest.raises(errors.DppArgparseFileNotFoundError):
        read_config(str(tmp_path / "foo.json"))


def test_read_config_invalid_json(tmp_path):
    dummy = tmp_path / CONFIG_NAME
    with open(dummy, "w+") as fp:
        fp.write("hello, world!")

    with pytest.raises(errors.DppArgparseInvalidConfigError):
        read_config(tmp_path)


def test_read_config_corrupted_json(tmp_path):
    dummy = tmp_path / CONFIG_NAME
    with open(dummy, "w+") as fp:
        obj = {"foo": 1}
        json.dump(obj, fp)

    with pytest.raises(errors.DppArgparseConfigCorruptedError):
        read_config(tmp_path)


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

    metadata, worktree = read_config(tmp_path)

    assert metadata.name == obj["project_name"]
    assert worktree.project_name == obj["project_name"]
    assert worktree.index == obj["index"]
    assert worktree.buggy == obj["buggy"]
    assert worktree.workspace == obj["workspace"]


def test_write_config(tmp_path):
    worktree = Worktree("yara", 1, True, str(tmp_path / "imaginary_path"))

    with pytest.raises(errors.DppArgparseFileNotFoundError):
        write_config(worktree)

    p = tmp_path / "yara" / "buggy#1"
    p.mkdir(parents=True)

    worktree = Worktree("yara", 1, True, str(tmp_path))
    write_config(worktree)

    with open(p / CONFIG_NAME, "r") as fp:
        config = json.load(fp)

    assert asdict(worktree) == config


def test_project_parser_invalid_project_should_throw(tmp_path):
    parser = create_common_project_parser()

    with pytest.raises(errors.DppArgparseNotProjectDirectory):
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
