from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [(1, 79), (2, 120), (3, 122), (4, 86), (5, 40)],
)
def test_xbps(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, auto_cleanup):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case, auto_cleanup)
