from defects4cpp.processor.action import Action


def test_check_help_attr():
    a = Action()
    assert hasattr(a, "help")
