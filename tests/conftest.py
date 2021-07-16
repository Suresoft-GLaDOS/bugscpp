import sys
from os import environ
from os.path import abspath, dirname, join

import pytest

root_dir = dirname(dirname(abspath(__file__)))
sys.path.extend([root_dir, join(root_dir, "defects4cpp")])


@pytest.fixture
def gitenv():
    environ["GIT_COMMITTER_NAME"] = "defects4cpp"
    environ["GIT_COMMITTER_EMAIL"] = "defects4cpp@email.com"
    yield
    del environ["GIT_COMMITTER_NAME"]
    del environ["GIT_COMMITTER_EMAIL"]
