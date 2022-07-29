from defects4cpp.command import CommandList
from defects4cpp.command import HelpCommand

def test_check_help_attr():
    commands = CommandList()
    assert "help" in commands

def test_check_help_help():
    helpCommand = HelpCommand()
    helpCommand.help

def test_check_help_run():
    helpCommand = HelpCommand()
    helpCommand.run([])
