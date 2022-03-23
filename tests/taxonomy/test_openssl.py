from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [
        (1, 46),
        # (2, 40),
        # (3, 119),
        # (4, 71),
        # (5, 97),
        # (6, 70),
        # (7, 28),
        # (8, 112),
        # (9, 110),
        # (10, 69),
        # (11, 68),
        # (12, 97),
        # (13, 57),
        # (14, 91),
        # (15, 66),
        # (16, 160),
        # (17, 204),
        # (18, 94),
        # (19, 46),
        # (20, 47),
        # (21, 128),
        # (22, 119),
        # (23, 124),
        # (24, 182),
        # (25, 110),
        # (26, 107),
        # (27, 113),
        # (28, 186),
        # (29, 207),
        # (30, 214),
        # (31, 126),
    ],
)
def test_openssl(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, auto_cleanup):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case, auto_cleanup)
