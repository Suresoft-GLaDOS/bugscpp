from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy


@pytest.mark.parametrize("defect", [(1, 23)])
def test_libssh(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys, auto_cleanup, uid, request):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case, capsys, auto_cleanup, uid, request)
