from defects4cpp.command import CommandList
from defects4cpp.command import ShowCommand

def test_check_show_attr():
    commands = CommandList()
    assert "show" in commands

def test_check_show_help():
    showCommand = ShowCommand()
    showCommand.help

def test_check_show_run():
    showCommand = ShowCommand()
    showCommand.run()


