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
def test_cppcheck(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys, auto_cleanup, uid, request,
                  start_from, end_to):
    index, case = defect
    test_dir = defect_path(index, case)

    if ((start_from is None) or (index >= int(start_from))) and \
       ((end_to is None) or (index <= int(end_to))):
        validate_taxonomy(test_dir, index, case, capsys, auto_cleanup, uid, request)
    else:
        pytest.skip(f"Skipping test (index:{index})")
