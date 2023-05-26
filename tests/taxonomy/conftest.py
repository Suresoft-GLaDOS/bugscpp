import errno
import json
import os
import re
import stat
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from typing import Callable

import pytest
import whatthepatch

from bugscpp.taxonomy import Taxonomy

# def get_defects(project):
#     t = Taxonomy()[project]
#
#     t = Taxonomy()
#     assert(project_name in t.__lazy_taxonomy.keys())
#
#     test_list = []
#     defects_num = len(t[project_name].defects)
#
#     for i in range(0, defects_num):
#         buggy_case = t[project_name].defects[i].case[0]
#         case_tuple = (i + 1, buggy_case)
#         test_list.append(case_tuple)
# return test_list


def pytest_generate_tests(metafunc):
    assert "project" in metafunc.fixturenames
    meta_project = Taxonomy()[metafunc.config.option.project]
    start_from = (
        int(metafunc.config.getoption("--start-from"))
        if metafunc.config.getoption("--start-from")
        else 1
    )
    end_to = (
        int(metafunc.config.getoption("--end-to"))
        if metafunc.config.getoption("--end-to")
        else len(meta_project.defects)
    )
    assert (
        start_from <= end_to
    ), f'"start_from"({start_from}) must be less than or equal to "end_to"({end_to})'
    metafunc.parametrize("index", [index for index in range(start_from, end_to + 1)])


def pytest_addoption(parser):
    parser.addoption(
        "--auto-cleanup",
        action="store_true",
        default=False,
        help="Automatically cleanup test directories after running tests.",
    )
    parser.addoption(
        "--uid", action="store", default="", help="Set uid of user defects4cpp."
    )
    parser.addoption(
        "--project", action="store", default="", required=True, help="Set project name."
    )
    parser.addoption(
        "--start-from", action="store", default="", help="Set test number start from"
    )
    parser.addoption(
        "--end-to", action="store", default="", help="Set test number end to"
    )
    parser.addoption(
        "--no-skip", action="store_true", default=False, help="Force to run tests"
    )


@pytest.fixture
def project(request):
    return request.config.getoption("--project")


@pytest.fixture
def auto_cleanup(request):
    return request.config.getoption("--auto-cleanup")


@pytest.fixture
def uid(request):
    return request.config.getoption("--uid")


@pytest.fixture
def no_skip(request):
    return request.config.getoption("--no-skip")


@dataclass
class TestDirectory:
    project: str
    checkout_dir: Path
    fixed_target_dir: Path
    buggy_target_dir: Path
    __test__ = False

    def fixed_output_dir(self, index: int, case: int):
        return self.checkout_dir / f"{self.project}-fixed-{str(index)}-{str(case)}"

    def buggy_output_dir(self, index: int, case: int):
        return self.checkout_dir / f"{self.project}-buggy-{str(index)}-{str(case)}"


@pytest.fixture
def defect_path(tmp_path: Path, request) -> Callable[[int], TestDirectory]:
    def create_defect_path(index: int) -> TestDirectory:
        # test_PROJECT_NAME
        project = request.config.getoption("--project")
        d = tmp_path / request.node.name
        d.mkdir(exist_ok=True)
        return TestDirectory(
            project,
            d,
            buggy_target_dir=(d / project / f"buggy#{index}"),
            fixed_target_dir=(d / project / f"fixed#{index}"),
        )

    return create_defect_path


def rmtree_onerror(func, path, exc) -> None:
    excvalue = exc[1]
    if func in (os.rmdir, os.unlink) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # chmod 0777
        func(path)  # Try the error causing delete operation again
    else:
        raise


@pytest.fixture(scope="function", autouse=True)
def cleanup(tmp_path: Path, auto_cleanup, capsys):
    if auto_cleanup:
        with capsys.disabled():
            print(f"cleanup {tmp_path} before yield")
    yield
    if auto_cleanup:
        with capsys.disabled():
            print(f"cleanup {tmp_path} after yield")
        try:
            rmtree(tmp_path, ignore_errors=False, onerror=rmtree_onerror)
        except PermissionError:
            pass
        except FileNotFoundError:
            pass


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


def get_patch_dict(buggy_defect):
    _patch_dict = {}
    assert not (buggy_defect.buggy_patch and buggy_defect.fixed_patch)
    if buggy_defect.buggy_patch and Path(buggy_defect.buggy_patch).exists():
        patch = buggy_defect.buggy_patch
        is_buggy = True
    elif buggy_defect.fixed_patch and Path(buggy_defect.fixed_patch).exists():
        patch = buggy_defect.fixed_patch
        is_buggy = False
    else:
        raise ValueError(f"Patch does not exists: {buggy_defect}")
    with open(patch, encoding="utf-8", newline=os.linesep) as f:
        buggy_patches = f.read()
        for diff in whatthepatch.parse_patch(buggy_patches):
            assert diff.header.new_path == diff.header.old_path
            path = diff.header.new_path
            buggy_lines, fixed_lines = [], []
            for change in diff.changes:
                if change.new is not None and change.old is None:
                    if is_buggy:
                        buggy_lines.append(change.new)
                    else:
                        fixed_lines.append(change.new)
                elif change.new is None and change.old is not None:
                    if is_buggy:
                        fixed_lines.append(change.old)
                    else:
                        buggy_lines.append(change.old)
            _patch_dict[path] = dict()
            _patch_dict[path]["buggy"] = buggy_lines
            _patch_dict[path]["fixed"] = fixed_lines
    return _patch_dict
