from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize("defect", [(1, 1), (2, 23), (3, 65)])
def test_wget2(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys, auto_cleanup):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case, capsys, auto_cleanup)
