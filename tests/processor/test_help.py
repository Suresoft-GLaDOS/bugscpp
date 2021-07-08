import defects4cpp.processor


def test_check_help_attr():
    commands = defects4cpp.processor.CommandList()
    assert "help" in commands
