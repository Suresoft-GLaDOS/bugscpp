import logging

import pytest
from message import message

from bugscpp.errors import DppGitCloneError


@pytest.fixture
def disable_pytest_logger():
    def disable():
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    return disable


def test_change_logger_path(
    tmp_path, disable_pytest_logger, meta_json, create_checkout
):
    disable_pytest_logger()

    path = tmp_path / "test.log"
    message.path = path
    checkout = create_checkout(meta_json)
    with pytest.raises(SystemExit) as wrapped_system_exit:
        checkout([])
    assert wrapped_system_exit.type == SystemExit
    assert wrapped_system_exit.value.code == 1

    with open(path, "r") as fp:
        assert len(fp.readlines()) > 0

    path = tmp_path
    message.path = path
    with pytest.raises(SystemExit) as wrapped_system_exit:
        checkout([])
    assert wrapped_system_exit.type == SystemExit
    assert wrapped_system_exit.value.code == 1

    with open(path / "defects4cpp.log", "r") as fp:
        assert len(fp.readlines()) > 0


def test_output_log_to_stdout(capsys):
    message.stdout_title("Hello, world!")
    captured = capsys.readouterr()

    assert "Hello, world!" in captured.out
