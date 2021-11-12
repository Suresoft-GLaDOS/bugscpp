from defects4cpp.command import CommandList


def test_check_show_attr():
    commands = CommandList()
    assert "show" in commands
