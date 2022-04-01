from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect", [(1, 55), (2, 232), (3, 102), (4, 233), (5, 255), (6, 238)]
)
def test_yara(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys, auto_cleanup, uid):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case, capsys, auto_cleanup, uid)
