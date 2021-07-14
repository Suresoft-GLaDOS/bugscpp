import pytest

import defects4cpp.processor


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
