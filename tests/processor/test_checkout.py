import logging
import shutil
from pathlib import Path

from processor.core.data import Worktree
from processor.checkout import CheckoutCommand


def test_git_clone_error(create_checkout, meta_json, caplog):
    caplog.set_level(logging.DEBUG)
    checkout = create_checkout(meta_json)

    checkout([])
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

    checkout([])
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

    checkout([])
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

    checkout([])
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

    checkout([])
    output = [
        record.message
        for record in caplog.records
        if record.name == "processor.checkout"
    ]
    assert "git-am failed" in output[-1]

def test_checkout_command():
    checkoutCommand = CheckoutCommand()
    assert(checkoutCommand.group == "v1")
    assert(checkoutCommand.help == "Get a specific defect snapshot")
