from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [
        (1, 82),
        (2, 82),
        (3, 82),
        (4, 82),
        (5, 82),
    ],
)
def test_libtiff(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)
