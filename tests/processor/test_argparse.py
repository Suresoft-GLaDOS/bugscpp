import json
from dataclasses import asdict

import errors
from processor.core.argparser import create_common_project_parser, create_common_vcs_parser, read_config, write_config
from processor.core.docker import Worktree

CONFIG_NAME = ".defects4cpp.json"


def test_read_config_not_exist(tmp_path):
    try:
        read_config(str(tmp_path / "foo.json"))
    except errors.DppFileNotFoundError:
        assert True
    else:
        assert False


def test_read_config_invalid_json(tmp_path):
    dummy = tmp_path / CONFIG_NAME
    with open(dummy, "w+") as fp:
        fp.write("hello, world!")

    try:
        read_config(tmp_path)
    except errors.DppInvalidConfigError:
        assert True
    else:
        assert False


def test_read_config_corrupted_json(tmp_path):
    dummy = tmp_path / CONFIG_NAME
    with open(dummy, "w+") as fp:
        obj = {"foo": 1}
        json.dump(obj, fp)

    try:
        read_config(tmp_path)
    except errors.DppConfigCorruptedError:
        assert True
    else:
        assert False


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
    try:
        write_config(worktree)
    except errors.DppFileNotFoundError:
        assert True
    else:
        assert False

    p = tmp_path / "yara" / "buggy#1"
    p.mkdir(parents=True)

    worktree = Worktree("yara", 1, True, str(tmp_path))
    write_config(worktree)

    with open(p / CONFIG_NAME, "r") as fp:
        config = json.load(fp)

    assert asdict(worktree) == config


def test_project_parser(tmp_path):
    parser = create_common_project_parser()
    project_name = "yara"

    try:
        parser.parse_args(f"{tmp_path} --coverage".split())
    except errors.DppTaxonomyNotProjectDirectory:
        assert True
    else:
        assert False

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


def test_vsc_parser(tmp_path):
    parser = create_common_vcs_parser()
    project_name = "yara"

    try:
        parser.parse_args("foobar 1 --buggy".split())
    except SystemExit:
        assert True
    else:
        assert False

    args = parser.parse_args(f"{project_name} 1 --buggy".split())
    metadata = args.metadata
    worktree = args.worktree

    assert metadata.name == project_name
    assert worktree.project_name == project_name
    assert worktree.index == 1
