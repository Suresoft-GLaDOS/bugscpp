import json
from pathlib import Path
from typing import Callable

import processor
import pytest

from tests.conftest import TestDirectory

CONFIG_NAME = ".defects4cpp.json"


def checkout_dir_valid(d: Path) -> bool:
    return (d / CONFIG_NAME).exists()


def should_pass(d: Path, case: int) -> bool:
    with open(d / f"{case}.test") as fp:
        test_result = fp.readline()
    return test_result == "passed"


def should_fail(d: Path, case: int) -> bool:
    with open(d / f"{case}.test") as fp:
        test_result = fp.readline()
    return test_result == "failed"


def should_create_gcov(d: Path):
    gcov_files = list(d.glob("*.gcov"))
    # TODO: validate contents of gcov?
    return len(gcov_files) > 0


def should_create_summary_json(d: Path):
    with open(d / f"summary.json") as fp:
        summary_json = json.load(fp)
    return len(summary_json["files"]) > 0


def validate_taxonomy(test_dir: TestDirectory, index: int, case: int):
    checkout = processor.CheckoutCommand()
    build = processor.BuildCommand()
    test = processor.TestCommand()

    # Test fix
    fixed_target_dir = test_dir.fixed_target_dir
    checkout(
        f"{test_dir.project} {index} --target {str(test_dir.checkout_dir)}".split()
    )
    assert checkout_dir_valid(fixed_target_dir)

    build(f"{str(fixed_target_dir)} --coverage".split())
    test(
        f"{str(fixed_target_dir)} --coverage --case {case} --output-dir {str(test_dir.checkout_dir)}".split()
    )

    fixed_output_dir = test_dir.fixed_output_dir
    assert should_pass(fixed_output_dir, case)
    assert should_create_gcov(fixed_output_dir)
    assert should_create_summary_json(fixed_output_dir)

    # Test buggy
    buggy_target_dir = test_dir.buggy_target_dir
    checkout(
        f"{test_dir.project} {index} --buggy --target {str(test_dir.checkout_dir)}".split()
    )
    assert checkout_dir_valid(buggy_target_dir)

    build(f"{str(buggy_target_dir)} --coverage".split())
    test(
        f"{str(buggy_target_dir)} --coverage --case {case} --output-dir {str(test_dir.checkout_dir)}".split()
    )

    buggy_output_dir = test_dir.buggy_output_dir
    assert should_fail(buggy_output_dir, case)
    assert should_create_gcov(buggy_output_dir)
    assert should_create_summary_json(buggy_output_dir)


@pytest.mark.parametrize(
    "defect", [(1, 55), (2, 232), (3, 102), (4, 233), (5, 255), (6, 238)]
)
def test_yara(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)


@pytest.mark.parametrize("defect", [(1, 23)])
def test_libssh(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)
