from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [
        (1, 366),
        (2, 1212),
        (3, 1623),
    ],
)
def test_libxml2(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)

