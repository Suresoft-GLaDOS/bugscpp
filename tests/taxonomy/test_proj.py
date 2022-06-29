from typing import Callable

import pytest

from tests.taxonomy.conftest import TestDirectory, validate_taxonomy, get_defects

PROJECT_NAME = 'proj'

@pytest.mark.parametrize(
    "defect", get_defects(PROJECT_NAME)
)
def test_proj(defect, defect_path: Callable[[int, int], TestDirectory], gitenv, capsys, auto_cleanup, uid, request,
              start_from, end_to):
    index, case = defect
    test_dir = defect_path(index, case)

    if ((start_from is None) or (index >= int(start_from))) and \
       ((end_to is None) or (index <= int(end_to))):
        validate_taxonomy(test_dir, index, case, capsys, auto_cleanup, uid, request)
    else:
        pytest.skip(f"Skipping test (index:{index})")
