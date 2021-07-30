from pathlib import Path

import processor

CONFIG_NAME = ".defects4cpp.json"


def test_check_build_attr():
    commands = processor.CommandList()
    assert "build" in commands


def test_build_test_fixed(tmp_path, gitenv):
    d = tmp_path / "test_build_fixed"
    d.mkdir()

    project = "yara"
    index = 1
    case = 55
    checkout_dir = d / project / f"fixed#{index}"

    checkout = processor.CheckoutCommand()
    checkout(f"{project} {index} --target {str(d)}".split())
    assert (checkout_dir / CONFIG_NAME).exists()

    build = processor.BuildCommand()
    build(f"{str(checkout_dir)}".split())
    assert not list(checkout_dir.glob("**/*.gcno"))

    test = processor.TestCommand()
    test(f"{str(checkout_dir)} --case {case} --output-dir {str(tmp_path)}".split())
    assert not list(tmp_path.glob("**/*.gcov"))

    output_dir: Path = tmp_path / f"{project}-fixed#{index}-{case}"
    index_output: Path = output_dir / f"{case}.output"
    index_test: Path = output_dir / f"{case}.test"
    assert index_output.stat().st_size != 0
    assert index_test.stat().st_size != 0
    with open(index_test, "r") as fp:
        line = fp.readline()
    assert line == "passed"


def test_build_test_fixed_with_coverage(tmp_path, gitenv):
    d = tmp_path / "test_build_fixed_with_coverage"
    d.mkdir()

    project = "yara"
    index = 1
    case = 55
    checkout_dir = d / project / f"fixed#{index}"

    checkout = processor.CheckoutCommand()
    checkout(f"{project} {index} --target {str(d)}".split())
    assert (checkout_dir / CONFIG_NAME).exists()

    build = processor.BuildCommand()
    build(f"{str(checkout_dir)} --coverage".split())
    assert list(checkout_dir.glob("**/*.gcno"))

    test = processor.TestCommand()
    test(
        f"{str(checkout_dir)} --coverage --case {case} --output-dir {str(tmp_path)}".split()
    )
    assert list(tmp_path.glob("**/*.gcov"))

    output_dir: Path = tmp_path / f"{project}-fixed#{index}-{case}"
    index_output: Path = output_dir / f"{case}.output"
    index_test: Path = output_dir / f"{case}.test"
    assert index_output.stat().st_size != 0
    assert index_test.stat().st_size != 0
    with open(index_test, "r") as fp:
        line = fp.readline()
    assert line == "passed"


def test_build_test_buggy(tmp_path, gitenv):
    d = tmp_path / "test_build_buggy"
    d.mkdir()

    project = "yara"
    index = 1
    # This is the buggy case.
    case = 55
    checkout_dir = d / project / f"buggy#{index}"

    checkout = processor.CheckoutCommand()
    checkout(f"{project} {index} --buggy --target {str(d)}".split())
    assert (checkout_dir / CONFIG_NAME).exists()

    build = processor.BuildCommand()
    build(f"{str(checkout_dir)}".split())
    assert not list(checkout_dir.glob("**/*.gcno"))

    test = processor.TestCommand()
    test(f"{str(checkout_dir)} --case {case} --output-dir {str(tmp_path)}".split())
    assert not list(tmp_path.glob("**/*.gcov"))

    output_dir: Path = tmp_path / f"{project}-buggy#{index}-{case}"
    index_output: Path = output_dir / f"{case}.output"
    index_test: Path = output_dir / f"{case}.test"
    assert index_output.stat().st_size != 0
    assert index_test.stat().st_size != 0
    with open(index_test, "r") as fp:
        line = fp.readline()
    assert line == "failed"


def test_build_test_buggy_with_coverage(tmp_path, gitenv):
    d = tmp_path / "test_build_buggy_with_coverage"
    d.mkdir()

    project = "yara"
    index = 1
    # This is the buggy case.
    case = 55
    checkout_dir = d / project / f"buggy#{index}"

    checkout = processor.CheckoutCommand()
    checkout(f"{project} {index} --buggy --target {str(d)}".split())
    assert (checkout_dir / CONFIG_NAME).exists()

    build = processor.BuildCommand()
    build(f"{str(checkout_dir)} --coverage".split())
    assert list(checkout_dir.glob("**/*.gcno"))

    test = processor.TestCommand()
    test(
        f"{str(checkout_dir)} --coverage --case {case} --output-dir {str(tmp_path)}".split()
    )
    assert list(tmp_path.glob("**/*.gcov"))

    output_dir: Path = tmp_path / f"{project}-buggy#{index}-{case}"
    index_output: Path = output_dir / f"{case}.output"
    index_test: Path = output_dir / f"{case}.test"
    assert index_output.stat().st_size != 0
    assert index_test.stat().st_size != 0
    with open(index_test, "r") as fp:
        line = fp.readline()
    assert line == "failed"
