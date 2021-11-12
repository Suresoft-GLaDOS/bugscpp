from defects4cpp.command import CommandList


def test_check_help_attr():
    commands = CommandList()
    assert "help" in commands
