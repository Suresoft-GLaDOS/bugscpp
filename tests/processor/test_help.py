import processor


def test_check_help_attr():
    commands = processor.CommandList()
    assert "help" in commands
