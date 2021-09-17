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


@pytest.mark.parametrize("defect", [(1, 3), (2, 34), (3, 29), (4, 3), (5, 28), (6, 34)])
def test_wireshark(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)


@pytest.mark.parametrize(
    "defect", [(1, 12), (2, 12), (3, 12), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1)]
)
def test_libchewing(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)


@pytest.mark.parametrize(
    "defect", [(1, 4), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1)]
)
def test_libucl(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)


@pytest.mark.parametrize("defect", [(1, 1), (2, 23), (3, 65)])
def test_wget2(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)


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
        (8, 112),
        (9, 110),
        (10, 69),
        (11, 68),
        (12, 97),
        (13, 57),
        (14, 91),
        (15, 66),
        (16, 160),
        (17, 204),
        (18, 94),
        (19, 46),
        (20, 47),
        (21, 128),
        (22, 119),
        (23, 124),
        (24, 182),
        (25, 110),
        (26, 107),
        (27, 113),
        (28, 186),
        (29, 207),
        (30, 214),
        (31, 126),
    ],
)
def test_openssl(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)


@pytest.mark.parametrize(
    "defect",
    [
        (1, 2),
        (2, 2),
        (3, 2),
        (4, 38),
        (5, 43),
        (6, 39),
        (7, 50),
        (8, 2),
        (9, 2),
        (10, 2),
        (11, 2),
        (12, 2),
        (13, 6),
        (14, 49),
        (15, 50),
        (16, 2),
        (17, 2),
        (18, 2),
        (19, 39),
        (20, 3),
        (21, 2),
        (22, 2),
        (23, 49),
        (24, 45),
        (25, 51),
        (26, 43),
        (27, 2),
    ],
)
def test_proj(defect, defect_path: Callable[[int, int], TestDirectory], gitenv):
    index, case = defect
    test_dir = defect_path(index, case)
    validate_taxonomy(test_dir, index, case)
