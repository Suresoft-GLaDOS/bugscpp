from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [
        (1, 3),
    ],
)
def test_example(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys):
    index, case = defect
    test_dir = defect_path(index, case)
    with capsys.disabled():
        validate_taxonomy(test_dir, index, case)
