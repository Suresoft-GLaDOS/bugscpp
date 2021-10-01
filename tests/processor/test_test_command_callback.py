import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Generator

import processor
import pytest

from processor.core.command import DockerCommandScript


@dataclass
class TestConfig:
    src_dir: Path
    output_dir: Path
    dest: List[Path]
    __test__ = False


@pytest.fixture
def setup(tmp_path: Path, request) -> Callable[[List[int]], TestConfig]:
    def create(case: List[int]) -> TestConfig:
        src_dir = tmp_path / request.node.name / "yara" / "fixed#1"
        src_dir.mkdir(parents=True, exist_ok=True)
        output_dir = tmp_path / request.node.name / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        dpp_config = src_dir / ".defects4cpp.json"
        with open(dpp_config, "w+") as fp:
            obj = {
                "project_name": "yara",
                "index": 1,
                "buggy": False,
                "workspace": str(src_dir.parents[1]),
            }
            json.dump(obj, fp)
        return TestConfig(
            src_dir, output_dir, [output_dir / f"yara-fixed#1-{i}" for i in case]
        )

    return create


def iterate_once(script_it: Generator[DockerCommandScript, None, None]):
    next(script_it)
    obj = next(script_it)
    next(script_it)
    return obj


def test_check_result(setup):
    test = processor.TestCommand()
    config = setup([1, 2])
    cmd = f"{str(config.src_dir)} --output-dir={str(config.output_dir)} --case 1,2".split()

    script_generator = test.create_script_generator(cmd)
    script_it = script_generator.create()

    # Command with zero exit code.
    a = iterate_once(script_it)
    a.lines = [""]
    a.output(1, 0, "hello world!")

    d1 = test.summary_dir(1)
    with open(f"{d1}/1.output", "r") as output:
        assert output.readline() == "hello world!"
    with open(f"{d1}/1.test", "r") as result:
        assert result.readline() == "passed"

    # Command with non-zero exit code.
    b = iterate_once(script_it)
    b.lines = [""]
    b.output(1, 1, "Bye world!")

    d2 = test.summary_dir(2)
    with open(f"{d2}/2.output", "r") as output:
        assert output.readline() == "Bye world!"
    with open(f"{d2}/2.test", "r") as result:
        assert result.readline() == "failed"


def test_check_coverage(setup):
    test = processor.TestCommand()
    config = setup([1])
    cmd = f"{str(config.src_dir)} --coverage --output-dir={str(config.output_dir)} --case 1".split()

    script_generator = test.create_script_generator(cmd)
    script_it = script_generator.create()

    # Create a dummy gcov directory.
    gcov = config.src_dir / "gcov"
    gcov.mkdir(parents=True, exist_ok=True)
    with open(f"{gcov}/foo.gcov", "w+") as fp:
        fp.write("Hello, world!")

    a = iterate_once(script_it)
    a.lines = [""]
    a.output(1, 0, "hello world!")

    # gcov directory should be removed.
    assert not gcov.exists()
    with open(test.summary_dir(1) / "foo.gcov", "r") as fp:
        assert fp.readline() == "Hello, world!"
    assert len(test.failed_coverage_files) == 0

    # Run again to see if it fails (there is no gcov directory).
    script_it = script_generator.create()

    a = iterate_once(script_it)
    a.lines = [""]
    a.output(1, 0, "hello world!")

    assert len(test.failed_coverage_files) > 0
