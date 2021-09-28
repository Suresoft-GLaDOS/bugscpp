from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [
        (1, 24),
        (2, 30),
        (3, 33),
        (4, 21),
        (5, 5),
        (6, 52),
        (7, 48),
        (8, 32),
        (9, 5),
        (10, 15),
        (11, 60),
        (12, 44),
        (13, 31),
        (14, 30),
        (15, 55),
        (16, 30),
        (17, 13),
        (18, 31),
        (19, 5),
        (20, 52),
        (21, 11),
        (22, 55),
        (23, 60),
        (24, 59),
        (25, 5),
        (26, 52),
        (27, 11),
        (28, 5),
        (29, 19),
        (30, 53),
    ],
)
def test_cppcheck(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)
