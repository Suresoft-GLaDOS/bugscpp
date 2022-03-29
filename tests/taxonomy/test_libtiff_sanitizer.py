from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize(
    "defect",
    [
        (1, 82),
        (2, 82),
        (3, 82)
    ],
)
def test_libtiff_sanitizer(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys, auto_cleanup):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case, capsys, auto_cleanup)
