import defects4cpp.processor
from defects4cpp.processor.action import Action


def test_check_build_attr():
    a = Action()
    assert hasattr(a, "build")


def test_build_command():
    cmd = defects4cpp.processor.BuildCommand()
    # cmd(["--project=libsndfile", "--no=0"])
