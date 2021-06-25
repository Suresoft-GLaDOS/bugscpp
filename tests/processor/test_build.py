from defects4cpp.processor.action import Action
from defects4cpp.processor.build import BuildCommand


def test_check_build_attr():
    a = Action()
    assert hasattr(a, "build")


def test_build_command():
    cmd = BuildCommand()
    cmd(["--project=libsndfile", "--no=0"])
