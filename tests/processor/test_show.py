from defects4cpp.processor.action import Action


def test_check_show_attr():
    a = Action()
    assert hasattr(a, "show")
