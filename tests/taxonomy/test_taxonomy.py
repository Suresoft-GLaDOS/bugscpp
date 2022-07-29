import json
import pytest
from pathlib import Path
from shutil import rmtree
from typing import Callable
from processor.build import BuildCommand
from processor.checkout import CheckoutCommand
from processor.test import TestCommand
from taxonomy import Taxonomy
from tests.taxonomy.conftest import TestDirectory, should_fail, read_captured_output, should_create_gcov, \
    should_create_summary_json, should_pass, get_patch_dict, rmtree_onerror

TAXONOMY_TEST_SKIP_LIST = [
    ("libchewing", 3),
    ("libxml2", 1),
    ("libxml2", 2),
    ("openssl", 9),
    ("openssl", 10),
    ("openssl", 12),
    ("openssl", 13),
    ("openssl", 14),
    ("openssl", 16),
    ("openssl", 19),
    ("openssl", 21),
    ("openssl", 22),
    ("openssl", 23),
    ("openssl", 26),
    ("openssl", 27),
    ("openssl", 28),
    ("proj", 23),
    ("proj", 24),
    ("wireshark", 3),
    ("yara", 4),
    ("yara", 5),
]

# GCOV_CHECK_SKIP_LIST = [
#     ("yara", 4)
# ]

BUGGY_LINE_CHECK_SKIP_LIST = [
    ("openssl", 8),
    ("openssl", 13),
    ("openssl", 23),
    ("openssl", 28),
    ("yara", 4)
]

CONFIG_NAME = '.defects4cpp.json'


def test_taxonomy(project, index, defect_path: Callable[[int], TestDirectory], gitenv, capsys, auto_cleanup, uid,
                  no_skip):
    if not no_skip and (project, index) in TAXONOMY_TEST_SKIP_LIST:
        pytest.skip(f"Skipping test for {(project, index)}. Will be fixed soon!")
    checkout = CheckoutCommand()
    build = BuildCommand()
    test = TestCommand()
    test_dir = defect_path(index)
    meta_project = Taxonomy()[project]
    failing_testcases = meta_project.defects[index - 1].case

    # Read patch information
    patch_dict = get_patch_dict(meta_project.defects[index - 1])
    number_of_all_patched_lines = 0
    for patch_path in patch_dict:
        number_of_all_patched_lines = len(patch_dict[patch_path]['buggy']) + len(patch_dict[patch_path]['fixed'])
    assert (number_of_all_patched_lines > 0)

    # check buggy (coverage) first
    checkout(f"{str(project)} {index} --buggy --target {str(test_dir.checkout_dir)}".split())
    checkout_dir_valid(test_dir.buggy_target_dir)
    build(f"{str(test_dir.buggy_target_dir)} -u {str(uid)} --coverage -v".split())
    test(
        f"{str(test_dir.buggy_target_dir)} "
        f"--coverage "
        f"--case {','.join([str(case) for case in failing_testcases])} "
        f"--output-dir {str(test_dir.checkout_dir)}".split()
    )
    for case in failing_testcases:
        buggy_output_dir = test_dir.buggy_output_dir(index, case)
        assert should_fail(buggy_output_dir, case), read_captured_output(buggy_output_dir, case)
        assert should_create_summary_json(buggy_output_dir)
        assert should_create_gcov(buggy_output_dir)
        with open(buggy_output_dir / "summary.json") as fp:
            summary_json = json.load(fp)
            all_file_paths_in_summary_json = [file["file"] for file in summary_json['files']]
            summary_dict = {summary_json['files'][i]['file']: summary_json['files'][i]['lines']
                            for i in range(len(summary_json['files']))}
            covered_buggy_lines = set()
            covered_lines_in_buggy_files = set()
            with capsys.disabled():
                for patched_file, patched_lines in patch_dict.items():
                    # find the file paths in summary json for the patched file
                    patched_file_paths = [fp for fp in all_file_paths_in_summary_json
                                          if Path(fp).name == Path(patched_file).name]
                    # if (project, index) in GCOV_CHECK_SKIP_LIST:
                    #     continue
                    assert len(patched_file_paths) == 1, \
                        f"Expected one file path for {patched_file}, but found {patched_file_paths}"
                    patched_file_path = patched_file_paths[0]

                    if len(patch_dict[patched_file]['buggy']) > 0:
                        # if patched_file has buggy lines in the patched file
                        # check if any buggy lines are covered
                        for line in summary_dict[patched_file_path]:
                            if line['line_number'] in patch_dict[patched_file]['buggy'] and line['count'] > 0:
                                covered_buggy_lines.add((patched_file_path, line['line_number']))
                    else:
                        # if patched_file does not have any buggy lines in the patched file,
                        # check if any fixed lines exists
                        assert (len(patch_dict[patched_file]['fixed']) > 0)
                        # weak testing: check if any lines in the fixed file are covered
                        for line in summary_dict[patched_file_path]:
                            if line['count'] > 0:
                                covered_lines_in_buggy_files.add((patched_file_path, line['line_number']))
                print(f"covered buggy lines: {covered_buggy_lines}")
                print(f"covered fixed lines: {covered_lines_in_buggy_files}")
                if (project, index) not in BUGGY_LINE_CHECK_SKIP_LIST:
                    assert (len(covered_buggy_lines) + len(covered_lines_in_buggy_files) > 0)
                else:
                    print(f"Skipping buggy line check for {project} {index}")
    # check test fails if and only if buggy cases are run
    test(
        f"{str(test_dir.buggy_target_dir)} "
        f"--coverage "
        f"--output-dir {str(test_dir.checkout_dir)}".split()
    )
    for case in range(1, len(meta_project.defects[index - 1].case) + 1):
        if case not in failing_testcases:
            buggy_output_dir = test_dir.buggy_output_dir(index, case)
            assert should_pass(buggy_output_dir, case), f"case:{case}" + read_captured_output(buggy_output_dir, case)

    if auto_cleanup:
        try:
            rmtree(test_dir.checkout_dir, ignore_errors=False, onerror=rmtree_onerror)
        except PermissionError:
            pass
        except FileNotFoundError:
            pass
    # get test_dir again becase it is cleaned up
    test_dir = defect_path(index)

    # check fixed (not coverage build)
    checkout(f"{str(project)} {index} --target {str(test_dir.checkout_dir)}".split())
    checkout_dir_valid(test_dir.fixed_target_dir)
    build(f"{str(test_dir.fixed_target_dir)} -u {str(uid)} -v".split())
    test(
        f"{str(test_dir.fixed_target_dir)} "
        f"--output-dir {str(test_dir.checkout_dir)}".split()
    )
    for case in range(1, len(meta_project.defects[index - 1].case) + 1):
        fixed_output_dir = test_dir.fixed_output_dir(index, case)
        assert should_pass(fixed_output_dir, case), f"case:{case}" + read_captured_output(fixed_output_dir, case)

    if auto_cleanup:
        try:
            rmtree(test_dir.checkout_dir, ignore_errors=False, onerror=rmtree_onerror)
        except PermissionError:
            pass
        except FileNotFoundError:
            pass


def checkout_dir_valid(d: Path) -> bool:
    return (d / CONFIG_NAME).exists()
