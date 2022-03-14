import json
import re
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from typing import Callable

import pytest

from defects4cpp.command import BuildCommand, CheckoutCommand, TestCommand

CONFIG_NAME = ".defects4cpp.json"


@dataclass
class TestDirectory:
    project: str
    checkout_dir: Path
    fixed_target_dir: Path
    fixed_output_dir: Path
    buggy_target_dir: Path
    buggy_output_dir: Path
    __test__ = False

# @pytest.fixture(scope="function", autouse=True)
# def cleanup(tmp_path: Path):
#     yield
#     try:
#         rmtree(tmp_path)
#     except FileNotFoundError:
#         pass
#     except PermissionError:
#         pass


@pytest.fixture
def defect_path(tmp_path: Path, request) -> Callable[[int, int], TestDirectory]:
    def create_defect_path(index: int, case: int) -> TestDirectory:
        # test_PROJECT_NAME
        regex = re.compile(r"test_(.*)\[.*]")
        project = regex.match(request.node.name).groups()[0]

        d = tmp_path / request.node.name
        d.mkdir()
        return TestDirectory(
            project,
            d,
            fixed_target_dir=(d / project / f"fixed#{index}"),
            fixed_output_dir=(d / f"{project}-fixed#{index}-{case}"),
            buggy_target_dir=(d / project / f"buggy#{index}"),
            buggy_output_dir=(d / f"{project}-buggy#{index}-{case}"),
        )

    return create_defect_path


def checkout_dir_valid(d: Path) -> bool:
    return (d / CONFIG_NAME).exists()


def read_captured_output(d: Path, case: int) -> str:
    with open(d / f"{case}.output") as fp:
        test_output = fp.readlines()
    return " ".join(test_output)


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
    with open(d / "summary.json") as fp:
        summary_json = json.load(fp)
    return len(summary_json["files"]) > 0


def validate_taxonomy(test_dir: TestDirectory, index: int, case: int):
    checkout = CheckoutCommand()
    build = BuildCommand()
    test = TestCommand()

    # Test fix
    fixed_target_dir = test_dir.fixed_target_dir
    checkout(
        f"{test_dir.project} {index} --target {str(test_dir.checkout_dir)}".split()
    )
    assert checkout_dir_valid(fixed_target_dir)

    build(f"{str(fixed_target_dir)} --coverage -v".split())
    test(
        f"{str(fixed_target_dir)} --coverage --case {case} --output-dir {str(test_dir.checkout_dir)}".split()
    )

    fixed_output_dir = test_dir.fixed_output_dir
    assert should_pass(fixed_output_dir, case), read_captured_output(
        fixed_output_dir, case
    )
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
    assert should_fail(buggy_output_dir, case), read_captured_output(
        buggy_output_dir, case
    )
    assert should_create_gcov(buggy_output_dir)
    assert should_create_summary_json(buggy_output_dir)
