from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize("defect", [(1, 1), (2, 56), (3, 22), (4, 29), (5, 42)])
def test_zsh(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, auto_cleanup):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case, auto_cleanup)
