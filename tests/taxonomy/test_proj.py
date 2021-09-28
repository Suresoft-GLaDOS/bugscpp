from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 38),
        (5, 43),
        (6, 39),
        (7, 50),
        (8, 2),
        (9, 2),
        (10, 2),
        (11, 2),
        (12, 2),
        (13, 6),
        (14, 49),
        (15, 50),
        (16, 2),
        (17, 2),
        (18, 2),
        (19, 39),
        (20, 3),
        (21, 2),
        (22, 2),
        (23, 49),
        (24, 45),
        (25, 51),
        (26, 43),
        (27, 2),
    ],
)
def test_proj(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)
