import defects4cpp.processor
import defects4cpp.taxonomy


def test_check_build_attr():
    commands = defects4cpp.processor.CommandList()
    assert "build" in commands


def test_build_fixed(tmp_path, gitenv):
    d = tmp_path / "test_build_fixed"
    d.mkdir()

    checkout = defects4cpp.processor.CheckoutCommand()
    build = defects4cpp.processor.BuildCommand()
    project = "yara"
    index = 1

    try:
        checkout(["--project", project, "--no", f"{index}", "--target", str(d)])
        build(["--project", project, "--no", f"{index}", "--target", str(d)])
    except:
        assert False
    else:
        assert not list((d / "yara" / "fixed#1").glob("**/*.gcno"))


def test_build_fixed_with_coverage(tmp_path, gitenv):
    d = tmp_path / "test_build_fixed_with_coverage"
    d.mkdir()

    checkout = defects4cpp.processor.CheckoutCommand()
    build = defects4cpp.processor.BuildCommand()
    project = "yara"
    index = 1

    try:
        checkout(["--project", project, "--no", f"{index}", "--target", str(d)])
        build(
            [
                "--coverage",
                "--project",
                project,
                "--no",
                f"{index}",
                "--target",
                str(d),
            ]
        )
    except:
        assert False
    else:
        assert list((d / "yara" / "fixed#1").glob("**/*.gcno"))


def test_build_buggy(tmp_path, gitenv):
    d = tmp_path / "test_build_buggy"
    d.mkdir()

    checkout = defects4cpp.processor.CheckoutCommand()
    build = defects4cpp.processor.BuildCommand()
    project = "yara"
    index = 1

    try:
        checkout(
            ["--project", project, "--no", f"{index}", "--buggy", "--target", str(d)]
        )
        build(["--project", project, "--no", f"{index}", "--buggy", "--target", str(d)])
    except:
        assert False
    else:
        assert not list((d / "yara" / "buggy#1").glob("**/*.gcno"))


def test_build_buggy_with_coverage(tmp_path, gitenv):
    d = tmp_path / "test_build_buggy_with_coverage"
    d.mkdir()

    checkout = defects4cpp.processor.CheckoutCommand()
    build = defects4cpp.processor.BuildCommand()
    project = "yara"
    index = 1

    try:
        checkout(
            ["--project", project, "--no", f"{index}", "--buggy", "--target", str(d)]
        )
        build(
            [
                "--coverage",
                "--project",
                project,
                "--no",
                f"{index}",
                "--buggy",
                "--target",
                str(d),
            ]
        )
    except:
        assert False
    else:
        assert list((d / "yara" / "buggy#1").glob("**/*.gcno"))
