import defects4cpp.processor


def test_check_show_attr():
    commands = defects4cpp.processor.CommandList()
    assert "show" in commands
