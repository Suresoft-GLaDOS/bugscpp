import argparse

import pytest

from bugscpp.command import TestCommand
from bugscpp.errors import DppAdditionalGcovOptionsWithoutCoverage
from bugscpp.processor.test import (CoverageTestCommandScript, GcovCommandScript, RunGcovrTestCommandScript,
                                    SetupTestCommandScript, TeardownTestCommandScript, TestCommandScript)

test_case = 0
test_type = ""
test_lines = [""]


def test_script_command():
    test_command_script = TestCommandScript(test_case, test_type, test_lines)
    test_command_script.before()
    test_command_script.step(0, "")
    test_command_script.after()


def test_setup_script_command():
    test_set = {0}
    setup_test_command = SetupTestCommandScript(test_set)
    setup_test_command.before()


def test_coverage_script_command():
    CoverageTestCommandScript(test_case, test_type, test_lines)


def test_tear_down_script_command():
    tear_down_test_command = TeardownTestCommandScript(test_case)
    tear_down_test_command.before()


def test_gcov_script_command():
    gcov_command = GcovCommandScript(test_case, test_type, test_lines)
    assert gcov_command.case == test_case
    gcov_command.before()
    gcov_command.step(0, "")
    gcov_command.output(1, 0, "")
    gcov_command.after()


def test_run_gcovr_script_command():
    run_gcovr_test_command = RunGcovrTestCommandScript(test_case, [""])
    run_gcovr_test_command.before()


def test_create_script_gernerator_command():
    test_command = TestCommand()
    with pytest.raises(DppAdditionalGcovOptionsWithoutCoverage):
        args = argparse.Namespace()
        args.coverage = False
        args.additional_gcov_options = True
        test_command.create_script_generator(args)


def test_help_command():
    test_command = TestCommand()
    assert test_command.help == "Run test"
