from bugscpp.command import CommandList, HelpCommand


def test_check_help_attr():
    commands = CommandList()
    assert "help" in commands


def test_check_help_help():
    helpCommand = HelpCommand()
    assert helpCommand.help == "Display help messages"


def test_check_help_run():
    helpCommand = HelpCommand()
    assert helpCommand.run([])
