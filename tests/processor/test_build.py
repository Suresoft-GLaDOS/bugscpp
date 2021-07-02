from pathlib import Path

import defects4cpp.processor


def test_check_build_attr():
    commands = defects4cpp.processor.CommandList()
    assert "build" in commands


def test_build_command():
    cmd = defects4cpp.processor.BuildCommand()
    project = "libsndfile"

    arguments = cmd.run(["--project", project, "--no", "0"])
    dockerfile = Path(arguments.dockerfile)

    assert dockerfile.name == "Dockerfile"
    assert dockerfile.parent.name == project
    assert arguments.commands
