import json
import re
import os
import errno
import stat
import whatthepatch
from dataclasses import dataclass
from pathlib import Path
from shutil import rmtree
from typing import Callable

import pytest
from defects4cpp.taxonomy import Taxonomy
from defects4cpp.command import BuildCommand, CheckoutCommand, TestCommand

CONFIG_NAME = ".defects4cpp.json"


def get_defects(project_name):
    t = Taxonomy()
    assert(project_name in t.__lazy_taxonomy.keys())

    test_list = []
    defects_num = len(t[project_name].defects)

    for i in range(0, defects_num):
        buggy_case = t[project_name].defects[i].case[0]
        case_tuple = (i + 1, buggy_case)
        test_list.append(case_tuple)

    return test_list

def pytest_addoption(parser):
    parser.addoption(
        "--auto-cleanup",
        action="store_true",
        default=False,
        help="Automatically cleanup test directories after running tests."
    )
    parser.addoption(
        "--uid",
        action="store",
        default="",
        help="Set uid of user defects4cpp."
    )
    parser.addoption(
        "--start-from",
        action="store",
        default="",
        help="Set test number start from"
    )
    parser.addoption(
        "--end-to",
        action="store",
        default="",
        help="Set test number end to"
    )


@pytest.fixture
def auto_cleanup(request):
    return request.config.getoption("--auto-cleanup")


@pytest.fixture
def uid(request):
    return request.config.getoption("--uid")


@pytest.fixture
def start_from(request):
    return request.config.getoption("--start-from")


@pytest.fixture
def end_to(request):
    return request.config.getoption("--end-to")


@dataclass
class TestDirectory:
    project: str
    checkout_dir: Path
    fixed_target_dir: Path
    fixed_output_dir: Path
    buggy_target_dir: Path
    buggy_output_dir: Path
    __test__ = False


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


def get_project_from_request(request):
    return re.compile(r"test_(.*)\[.*]").match(request.node.name).groups()[0]


@pytest.fixture
def defect_path(tmp_path: Path, request) -> Callable[[int, int], TestDirectory]:
    def create_defect_path(index: int, case: int) -> TestDirectory:
        # test_PROJECT_NAME
        project = get_project_from_request(request)

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


def validate_taxonomy(test_dir: TestDirectory, index: int, case: int, capsys, auto_cleanup, uid, request):
    checkout = CheckoutCommand()
    build = BuildCommand()
    test = TestCommand()
    project = get_project_from_request(request)
    is_coverage_check_skip = (project, index) in coverage_check_skip_list
    # Test fix
    fixed_target_dir = test_dir.fixed_target_dir
    checkout(
        f"{test_dir.project} {index} --target {str(test_dir.checkout_dir)}".split()
    )
    assert checkout_dir_valid(fixed_target_dir)
    build(f"{str(fixed_target_dir)} -u {str(uid)} --coverage -v".split())
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
    checkout_buggy_cmd = f"{test_dir.project} {index} --buggy --target {str(test_dir.checkout_dir)}".split()
    checkout(checkout_buggy_cmd)
    assert checkout_dir_valid(buggy_target_dir)

    buggy_checkout_args = checkout.parser.parse_args(checkout_buggy_cmd)
    buggy_defect = buggy_checkout_args.metadata.defects[buggy_checkout_args.index - 1]
    # read patch information

    patch_dict = get_patch_dict(buggy_defect)
    number_of_all_patched_lines = 0
    for patch_path in patch_dict:
        number_of_all_patched_lines = len(patch_dict[patch_path]['buggy']) + len(patch_dict[patch_path]['fixed'])
    assert(number_of_all_patched_lines > 0)

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

    if is_coverage_check_skip:
        with capsys.disabled():
            print(f"Skipping coverage check for {project} {index}")
    else:
        with open(buggy_output_dir / "summary.json") as fp:
            summary_json = json.load(fp)
            for patched_file, patched_lines in patch_dict.items():
                # Each 'file' value is relatrive to '/home/workspace'
                all_file_paths_in_summary_json = [file["file"] for file in summary_json['files']]
                with capsys.disabled():
                    if len([file for file in all_file_paths_in_summary_json if file == patched_file]) != 1:
                        print(f"!!!!! {patched_file} is not in summary.json (len="
                              f"{len([file for file in all_file_paths_in_summary_json])})")
                        continue
                    else:
                        print(
                            f"!!!!! {patched_file} is in summary.json")
                buggy_lines = patch_dict[patched_file]['buggy']
                if buggy_lines:
                    any_buggy_line_covered = False
                    for line in [file for file in summary_json['files'] if file['file'] == patched_file][0]['lines']:
                        if line['line_number'] in buggy_lines:
                            any_buggy_line_covered = True
                            with capsys.disabled():
                                print(f"##### buggy,{patched_file},{line}")
                    assert any_buggy_line_covered
                fixed_lines = patch_dict[patched_file]['fixed']
                if fixed_lines:
                    any_fixed_line_covered = False
                    for line in [file for file in summary_json['files'] if file['file'] == patched_file][0]['lines']:
                        if line['line_number'] in fixed_lines:
                            any_fixed_line_covered = True
                            with capsys.disabled():
                                print(f"##### fixed,{patched_file},{line}")
                    assert any_fixed_line_covered

    if auto_cleanup:
        for path in (test_dir.buggy_output_dir, test_dir.buggy_target_dir,
                     test_dir.fixed_output_dir, test_dir.fixed_target_dir):
            try:
                rmtree(path, ignore_errors=False, onerror=rmtree_onerror)
            except PermissionError:
                pass
            except FileNotFoundError:
                pass


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
    with open(patch, encoding='utf-8', newline=os.linesep) as f:
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
            _patch_dict[path]['buggy'] = buggy_lines
            _patch_dict[path]['fixed'] = fixed_lines
    return _patch_dict
