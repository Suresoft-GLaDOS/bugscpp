from bugscpp.command import CommandList, ShowCommand


def test_check_show_attr():
    commands = CommandList()
    assert "show" in commands


def test_check_show_help():
    showCommand = ShowCommand()
    assert showCommand.help == "Display defect taxonomies status"


def test_check_show_run(capsys):
    showCommand = ShowCommand()
    assert "example" not in capsys.readouterr()
