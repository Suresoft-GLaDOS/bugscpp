from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect", [(1, 12), (2, 12), (3, 12), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1)]
)
def test_libchewing(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)
