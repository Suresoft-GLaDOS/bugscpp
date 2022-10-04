import json
from pathlib import Path
from shutil import rmtree
from typing import Callable

import pytest
from processor.build import BuildCommand
from processor.checkout import CheckoutCommand
from processor.test import TestCommand
from taxonomy import Taxonomy

from tests.taxonomy.conftest import (TestDirectory, get_patch_dict, read_captured_output, rmtree_onerror,
                                     should_create_gcov, should_create_summary_json, should_fail, should_pass)

TAXONOMY_TEST_SKIP_LIST = []

BUGGY_LINE_CHECK_SKIP_LIST = []

CONFIG_NAME = ".defects4cpp.json"


def test_taxonomy(
    project,
    index,
    defect_path: Callable[[int], TestDirectory],
    gitenv,
    capsys,
    auto_cleanup,
    uid,
    no_skip,
):
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
        number_of_all_patched_lines = len(patch_dict[patch_path]["buggy"]) + len(
            patch_dict[patch_path]["fixed"]
        )
    assert number_of_all_patched_lines > 0

    # check buggy (coverage) first
    checkout(
        f"{str(project)} {index} --buggy --target {str(test_dir.checkout_dir)}".split()
    )
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
        assert should_fail(buggy_output_dir, case), read_captured_output(
            buggy_output_dir, case
        )
        assert should_create_summary_json(buggy_output_dir)
        assert should_create_gcov(buggy_output_dir)
        with open(buggy_output_dir / "summary.json") as fp:
            summary_json = json.load(fp)
            all_file_paths_in_summary_json = [
                file["file"] for file in summary_json["files"]
            ]
            summary_dict = {
                summary_json["files"][i]["file"]: summary_json["files"][i]["lines"]
                for i in range(len(summary_json["files"]))
            }
            covered_buggy_lines = set()
            covered_lines_in_buggy_files = set()
            with capsys.disabled():
                covered_file_count = 0
                for patched_file, patched_lines in patch_dict.items():
                    # find the file paths in summary json for the patched file
                    patched_file_paths = [
                        fp
                        for fp in all_file_paths_in_summary_json
                        if Path(fp).name == Path(patched_file).name
                    ]
                    if len(patched_file_paths) == 0:
                        continue
                    if len(patched_file_paths) > 1:
                        for fp in patched_file_paths:
                            if Path(fp) == Path(patched_file):
                                patched_file_paths = [patched_file]
                                break
                    # if (project, index) in GCOV_CHECK_SKIP_LIST:
                    #     continue
                    patched_file_path = patched_file_paths[0]

                    if len(patch_dict[patched_file]["buggy"]) > 0:
                        # if patched_file has buggy lines in the patched file
                        # check if any buggy lines are covered
                        for line in summary_dict[patched_file_path]:
                            if (
                                line["line_number"] in patch_dict[patched_file]["buggy"]
                                and line["count"] > 0
                            ):
                                covered_buggy_lines.add(
                                    (patched_file_path, line["line_number"])
                                )
                        if len(covered_buggy_lines) == 0:
                            # only if buggy lines are not covered but test is failed,
                            # check if any covered line exists
                            for line in summary_dict[patched_file_path]:
                                if line["count"] > 0:
                                    covered_lines_in_buggy_files.add(
                                        (patched_file_path, line["line_number"])
                                    )
                    else:
                        # if patched_file does not have any buggy lines in the patched file,
                        # check if any fixed lines exists
                        assert len(patch_dict[patched_file]["fixed"]) > 0
                        # weak testing: check if any lines in the fixed file are covered
                        for line in summary_dict[patched_file_path]:
                            if line["count"] > 0:
                                covered_lines_in_buggy_files.add(
                                    (patched_file_path, line["line_number"])
                                )
                    covered_file_count += 1
                assert covered_file_count > 0, f"Covered file should be larger than 0"
                print(f"covered buggy lines: {covered_buggy_lines}")
                print(f"covered fixed lines: {covered_lines_in_buggy_files}")
                if (project, index) not in BUGGY_LINE_CHECK_SKIP_LIST:
                    assert (
                        len(covered_buggy_lines) + len(covered_lines_in_buggy_files) > 0
                    )
                else:
                    print(f"Skipping buggy line check for {project} {index}")
    # check test fails if and only if buggy cases are run
    test(
        f"{str(test_dir.buggy_target_dir)} "
        f"--coverage "
        f"--output-dir {str(test_dir.checkout_dir)}".split()
    )
    buggy_is_pass_list = []
    for case in range(1, int(meta_project.defects[index - 1].num_cases) + 1):
        if case not in failing_testcases:
            buggy_output_dir = test_dir.buggy_output_dir(index, case)
            buggy_is_pass_list.append((case, should_pass(buggy_output_dir, case)))
    assert all(
        result[1] for result in buggy_is_pass_list
    ), f"buggy_is_pass_list = {buggy_is_pass_list}\n" + str(
        [
            read_captured_output(test_dir.buggy_output_dir(index, result[0]), result[0])
            for result in buggy_is_pass_list
            if not result[1]
        ]
    )
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
    fixed_is_pass_list = []
    for case in range(1, int(meta_project.defects[index - 1].num_cases) + 1):
        fixed_output_dir = test_dir.fixed_output_dir(index, case)
        fixed_is_pass_list.append((case, should_pass(fixed_output_dir, case)))
    assert all(
        result[1] for result in fixed_is_pass_list
    ), f"fixed_is_pass_list = {fixed_is_pass_list}\n" + str(
        [
            read_captured_output(test_dir.fixed_output_dir(index, result[0]), result[0])
            for result in fixed_is_pass_list
            if not result[1]
        ]
    )

    if auto_cleanup:
        try:
            rmtree(test_dir.checkout_dir, ignore_errors=False, onerror=rmtree_onerror)
        except PermissionError:
            pass
        except FileNotFoundError:
            pass


def checkout_dir_valid(d: Path) -> bool:
    return (d / CONFIG_NAME).exists()
