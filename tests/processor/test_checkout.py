import os

import pytest

import defects4cpp.processor


@pytest.fixture
def gitenv():
    os.environ["GIT_COMMITTER_NAME"] = "defects4cpp"
    os.environ["GIT_COMMITTER_EMAIL"] = "defects4cpp@email.com"
    yield
    del os.environ["GIT_COMMITTER_NAME"]
    del os.environ["GIT_COMMITTER_EMAIL"]


def test_checkout_fixed(tmp_path, gitenv):
    cmd = defects4cpp.processor.CheckoutCommand()
    project = "libsndfile"
    number = "1"
    # Run twice
    cmd(["--project", project, "--no", number, "--target", str(tmp_path)])
    cmd(["--project", project, "--no", number, "--target", str(tmp_path)])


def test_checkout_buggy(tmp_path, gitenv):
    cmd = defects4cpp.processor.CheckoutCommand()
    project = "libsndfile"
    number = "1"
    # Run twice
    cmd(["--project", project, "--no", number, "--buggy", "--target", str(tmp_path)])
    cmd(["--project", project, "--no", number, "--buggy", "--target", str(tmp_path)])
