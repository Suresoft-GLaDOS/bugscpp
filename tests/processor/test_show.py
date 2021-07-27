import processor


def test_check_show_attr():
    commands = processor.CommandList()
    assert "show" in commands
