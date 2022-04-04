from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [
        (1, 46),
        (2, 40),
        (3, 119),
        (4, 71),
        (5, 97),
        (6, 70),
        (7, 28),
        (8, 110),
        (9, 69),
        (10, 68),
        (11, 97),
        (12, 57),
        (13, 91),
        (14, 66),
        (15, 160),
        (16, 204),
        (17, 46),
        (18, 47),
        (19, 128),
        (20, 119),
        (21, 124),
        (22, 182),
        (23, 110),
        (24, 113),
        (25, 186),
        (26, 207),
        (27, 214),
        (28, 126),
    ],
)
def test_openssl(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys, auto_cleanup, uid, request,
                 start_from, end_to):
    index, case = defect
    test_dir = defect_path(index, case)

    if ((start_from is None) or (index >= int(start_from))) and \
       ((end_to is None) or (index <= int(end_to))):
        validate_taxonomy(test_dir, index, case, capsys, auto_cleanup, uid, request)
    else:
        pytest.skip(f"Skipping test (index:{index})")
