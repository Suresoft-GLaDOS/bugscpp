from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect", [(1, 4), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
)
def test_libucl(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys, auto_cleanup):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case, capsys, auto_cleanup)
