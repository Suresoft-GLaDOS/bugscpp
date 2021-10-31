import logging

import pytest
from message import message


@pytest.fixture
def disable_pytest_logger():
    def disable():
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

    return disable


def test_change_logger_path(tmp_path, disable_pytest_logger):
    disable_pytest_logger()

    path = tmp_path / "test.log"
    message.path = path
    message.warning(__name__, "Hello, world!")

    with open(path, "r") as fp:
        assert "Hello, world!" in fp.readline()

    path = tmp_path
    message.path = path
    message.warning(__name__, "Hello, world!")

    with open(path / "defects4cpp.log", "r") as fp:
        assert "Hello, world!" in fp.readline()


def test_output_log_to_stdout(capsys):
    message.stdout_title("Hello, world!")
    captured = capsys.readouterr()

    assert "Hello, world!" in captured.out
