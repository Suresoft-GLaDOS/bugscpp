import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Generator, List, Optional

import pytest
from processor.core.command import DockerCommand, DockerCommandScript, DockerCommandScriptGenerator
from processor.core.docker import Worktree
from taxonomy.taxonomy import CommandType, MetaData, Taxonomy

from bugscpp.command import TestCommand

_DUMMY_DOCKERFILE = """
FROM ubuntu:20.04

RUN useradd --uid 1001 --home-dir /home/workspace --shell /bin/bash defects4cpp
USER defects4cpp
ENV USER defects4cpp
WORKDIR /home/workspace
"""

_TEST_PROJECT_NAME = "yara"


class DummyDockerCommand(DockerCommand):
    _ignore_registry = True

    def __init__(
        self,
        callback,
        command_type: CommandType,
        commands: List[str],
        tmp: Path,
    ):
        parser = argparse.ArgumentParser()
        # Put default arguments here if something's been changed.
        parser.set_defaults(**{"env": None, "rebuild_image": False, "jobs": 1})

        super().__init__(parser)
        self.callback = callback
        self.command_type = command_type
        self.commands = commands
        self.metadata = MetaData(_TEST_PROJECT_NAME, str(tmp))
        self.worktree = Worktree(_TEST_PROJECT_NAME, 1, False, str(tmp))

        with open(f"{self.metadata.dockerfile}", "w+") as fp:
            fp.write(_DUMMY_DOCKERFILE)

    def create_script_generator(
        self, args: argparse.Namespace
    ) -> DockerCommandScriptGenerator:
        return DummyDockerCommandScriptGenerator(
            self.callback,
            self.command_type,
            self.commands,
            self.metadata,
            self.worktree,
        )

    def setup(self, generator: DockerCommandScriptGenerator):
        pass

    def teardown(self, generator: DockerCommandScriptGenerator):
        pass

    @property
    def help(self) -> str:
        return "help"


class DummyDockerCommandScriptGenerator(DockerCommandScriptGenerator):
    def __init__(
        self,
        callback: Callable,
        command_type: CommandType,
        commands: List[str],
        metadata: MetaData,
        worktree: Worktree,
    ):
        super().__init__(metadata, worktree, False)
        self.callback = callback
        self.command_type = command_type
        self.commands = commands

    def create(self) -> Generator[DockerCommandScript, None, None]:
        yield DummyDockerCommandScript(self.callback, self.command_type, self.commands)


class DummyDockerCommandScript(DockerCommandScript):
    def __init__(
        self, callback: Callable, command_type: CommandType, command: List[str]
    ):
        super().__init__(command_type, command)
        self.callback = callback

    def before(self):
        pass

    def step(self, linenr: int, line: str):
        pass

    def output(self, linenr: int, exit_code: Optional[int], output: str):
        self.callback(linenr, exit_code, output)

    def after(self):
        pass


@dataclass
class TestConfig:
    tmp: Path
    src_dir: Path
    output_dir: Path
    dest: List[Path]
    __test__ = False


@pytest.fixture
def setup(tmp_path: Path, request) -> Callable[[List[int]], TestConfig]:
    def create(case: List[int]) -> TestConfig:
        tmp = tmp_path / request.node.name
        src_dir = tmp / _TEST_PROJECT_NAME / "fixed-1"
        src_dir.mkdir(parents=True, exist_ok=True)
        output_dir = tmp / "output"
        output_dir.mkdir(parents=True, exist_ok=True)

        dpp_config = src_dir / ".defects4cpp.json"
        with open(dpp_config, "w+") as fp:
            obj = {
                "project_name": _TEST_PROJECT_NAME,
                "index": 1,
                "buggy": False,
                "workspace": str(src_dir.parents[1]),
            }
            json.dump(obj, fp)
        return TestConfig(
            tmp,
            src_dir,
            output_dir,
            [output_dir / f"{_TEST_PROJECT_NAME}-fixed-1-{i}" for i in case],
        )

    return create


def iterate_once(script_it: Generator[DockerCommandScript, None, None]):
    next(script_it)
    return next(script_it)


def iterate_coverage_once(script_it: Generator[DockerCommandScript, None, None]):
    next(script_it)
    next(script_it)
    obj = next(script_it)
    next(script_it)
    next(script_it)
    return obj


def test_check_result(setup):
    test = TestCommand()
    config = setup([1, 2])
    cmd = f"{str(config.src_dir)} --output-dir={str(config.output_dir)} --case 1,2".split()

    script_generator = test.create_script_generator(test.parser.parse_args(cmd))
    script_it = script_generator.create()

    # Command with zero exit code.
    a = iterate_once(script_it)
    a.lines = [""]
    a.output(1, 0, "hello world!")

    d1 = config.dest[0]
    with open(f"{d1}/1.output", "r") as output:
        assert output.readline() == "hello world!"
    with open(f"{d1}/1.test", "r") as result:
        assert result.readline() == "passed"

    # Command with non-zero exit code.
    b = iterate_once(script_it)
    b.lines = [""]
    b.output(1, 1, "Bye world!")

    d2 = config.dest[1]
    with open(f"{d2}/2.output", "r") as output:
        assert output.readline() == "Bye world!"
    with open(f"{d2}/2.test", "r") as result:
        assert result.readline() == "failed"


@pytest.mark.skip(reason="Temporarily disabled. Should be ran on Docker.")
def test_check_coverage(setup):
    test = TestCommand()
    config = setup([1])
    cmd = f"{str(config.src_dir)} --coverage --output-dir={str(config.output_dir)} --case 1".split()

    script_generator = test.create_script_generator(test.parser.parse_args(cmd))
    script_it = script_generator.create()

    # Create a dummy gcov directory.
    gcov = config.src_dir / "gcov"
    gcov.mkdir(parents=True, exist_ok=True)
    with open(f"{gcov}/foo.gcov", "w+") as fp:
        fp.write("Hello, world!")

    a = iterate_coverage_once(script_it)
    a.lines = [""]
    a.output(1, 0, "hello world!")

    # Now callback does not remove gcov file by callback
    # assert not gcov.exists()
    gcov.rmdir()

    with open(config.dest[0] / "foo.gcov", "r") as fp:
        assert fp.readline() == "Hello, world!"
    assert len(test.failed_coverage_files) == 0

    # Run again to see if it fails (there is no gcov directory).
    script_it = script_generator.create()

    a = iterate_coverage_once(script_it)
    a.lines = [""]
    a.output(1, 0, "hello world!")

    assert len(test.failed_coverage_files) > 0


@pytest.mark.slow
def test_run_command(setup):
    def docker_command_type_should_pass(_: Optional[int], exit_code: int, output: str):
        assert exit_code == 0
        assert output.strip() == "Hello, world!"

    def docker_command_type_should_fail_to_keep_context(
        linenr: Optional[int], exit_code: int, output: str
    ):
        if linenr == 1:
            # export TEST_VAR=1 won't work
            assert exit_code != 0
        elif linenr == 2:
            # TEST_VAR is not set
            assert exit_code == 0
            assert output.strip() == "$TEST_VAR"
        else:
            assert False, "unexpected line, check test input again"

    config = setup([1])
    test = DummyDockerCommand(
        callback=docker_command_type_should_pass,
        command_type=CommandType.Docker,
        commands=["echo 'Hello, world!'"],
        tmp=config.tmp,
    )
    test([])

    test = DummyDockerCommand(
        callback=docker_command_type_should_fail_to_keep_context,
        command_type=CommandType.Docker,
        commands=["export TEST_VAR=1", "echo $TEST_VAR"],
        tmp=config.tmp,
    )
    test([])


@pytest.mark.slow
def test_run_command_as_script(setup):
    def script_command_type_should_pass(_: Optional[int], exit_code: int, output: str):
        assert exit_code == 0
        assert output.strip() == "Hello, world!"

    def script_command_type_should_keep_context(
        linenr: Optional[int], exit_code: int, output: str
    ):
        assert linenr is None
        assert exit_code == 0
        assert output.strip() == "1"

    config = setup([1])
    test = DummyDockerCommand(
        callback=script_command_type_should_pass,
        command_type=CommandType.Script,
        commands=["#!/usr/bin/env bash", "echo 'Hello, world!'"],
        tmp=config.tmp,
    )
    test([])

    test = DummyDockerCommand(
        callback=script_command_type_should_keep_context,
        command_type=CommandType.Script,
        commands=["#!/usr/bin/env bash", "export TEST_VAR=1", "echo $TEST_VAR"],
        tmp=config.tmp,
    )
    test([])


@pytest.mark.slow
def test_additional_gcov_options(setup):
    test = TestCommand()
    t = Taxonomy()
    for defect in t:
        with open(Path(t.base) / defect / "meta.json") as meta_json:
            meta = json.load(meta_json)
            gcov_data = str(meta["common"]["gcov"]["commands"]).split(" ")
            for index in range(len(gcov_data)):
                if gcov_data[index] == "gcov":
                    assert gcov_data[index + 1] == "@DPP_ADDITIONAL_GCOV_OPTIONS@"
