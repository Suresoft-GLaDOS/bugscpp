import logging
import shutil
from pathlib import Path

import pytest
from processor.checkout import CheckoutCommand
from processor.core.data import Worktree


def test_git_clone_error(create_checkout, meta_json, caplog):
    caplog.set_level(logging.DEBUG)
    checkout = create_checkout(meta_json)

    with pytest.raises(SystemExit) as wrapped_system_exit:
        checkout([])
    assert wrapped_system_exit.type == SystemExit
    assert wrapped_system_exit.value.code == 1
    output = [
        record.message
        for record in caplog.records
        if record.name == "processor.checkout"
    ]
    assert "git-clone failed" in output[-1]


def test_git_worktree_error(create_checkout, meta_json, caplog):
    caplog.set_level(logging.DEBUG)
    meta_json["info"]["url"] = "https://github.com/Suresoft-GLaDOS/defects4cpp-test"
    # Invalid hash value
    meta_json["defects"][0]["hash"] = "1"
    checkout = create_checkout(meta_json)

    with pytest.raises(SystemExit) as wrapped_system_exit:
        checkout([])
    assert wrapped_system_exit.type == SystemExit
    assert wrapped_system_exit.value.code == 1
    output = [
        record.message
        for record in caplog.records
        if record.name == "processor.checkout"
    ]
    assert "git-worktree failed" in output[-1]


def test_git_checkout_error(create_checkout, meta_json, caplog):
    caplog.set_level(logging.DEBUG)
    meta_json["info"]["url"] = "https://github.com/Suresoft-GLaDOS/defects4cpp-test"
    meta_json["defects"][0]["hash"] = "0a158cb95d7ed8e64552ef80df6e6204205d4fa5"
    checkout = create_checkout(meta_json)

    # Create a directory ahead to raise exception.
    worktree: Worktree = checkout.parser.parse_args([]).worktree
    worktree.host.mkdir(parents=True, exist_ok=True)

    with pytest.raises(SystemExit) as wrapped_system_exit:
        checkout([])
    assert wrapped_system_exit.type == SystemExit
    assert wrapped_system_exit.value.code == 1
    output = [
        record.message
        for record in caplog.records
        if record.name == "processor.checkout"
    ]
    assert "git-checkout failed" in output[-1]


def test_git_submodule_init_error(create_checkout, meta_json, caplog):
    caplog.set_level(logging.DEBUG)
    meta_json["info"]["url"] = "https://github.com/Suresoft-GLaDOS/defects4cpp-test"
    meta_json["defects"][0]["hash"] = "0a158cb95d7ed8e64552ef80df6e6204205d4fa5"
    checkout = create_checkout(meta_json)

    with pytest.raises(SystemExit) as wrapped_system_exit:
        checkout([])
    assert wrapped_system_exit.type == SystemExit
    assert wrapped_system_exit.value.code == 1
    output = [
        record.message
        for record in caplog.records
        if record.name == "processor.checkout"
    ]
    assert "git-submodule failed" in output[-1]


def test_git_apply_patch_error_patch_could_not_be_applied(
    create_checkout, meta_json, resource_dir, caplog
):
    caplog.set_level(logging.DEBUG)
    meta_json["info"]["url"] = "https://github.com/Suresoft-GLaDOS/defects4cpp-test"
    meta_json["defects"][0]["hash"] = "0935324da04784d625c5faef0705adf8705fab9c"
    checkout = create_checkout(meta_json)

    worktree: Worktree = checkout.parser.parse_args([]).worktree
    patch = resource_dir / "corrupted-test.patch"
    dest = Path(worktree.workspace) / "patch" / "0001-common.patch"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy(patch, str(dest))

    with pytest.raises(SystemExit) as wrapped_system_exit:
        checkout([])
    assert wrapped_system_exit.type == SystemExit
    assert wrapped_system_exit.value.code == 1
    output = [
        record.message
        for record in caplog.records
        if record.name == "processor.checkout"
    ]
    assert "git-am failed" in output[-1]


def test_checkout_command():
    checkout_command = CheckoutCommand()
    assert checkout_command.group == "v1"
    assert checkout_command.help == "Get a specific defect snapshot"
