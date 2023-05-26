import time
from pathlib import Path

import docker.errors
import pytest

from bugscpp.command import BuildCommand, CheckoutCommand
from bugscpp.config import config


@pytest.mark.parametrize(
    "coverage,export,expected",
    [
        (True, True, f"coverage_command {config.DPP_COMPILATION_DB_TOOL}"),
        (True, False, "coverage_command"),
        (False, True, f"{config.DPP_COMPILATION_DB_TOOL} command"),
        (False, False, "command"),
    ],
)
def test_build_command_should_generate_command_based_on_options(
    create_build, meta_json, coverage, export, expected
):
    meta_json["common"]["build"]["commands"][0]["lines"] = [
        "@DPP_COMPILATION_DB_TOOL@ command"
    ]
    meta_json["common"]["build-coverage"]["commands"][0]["lines"] = [
        "coverage_command @DPP_COMPILATION_DB_TOOL@"
    ]
    build = create_build(meta_json, {"coverage": coverage, "export": export})
    generator = build.create_script_generator(build.parser.parse_args([]))

    for script in generator.create():
        assert len(script.lines) == 1
        assert script.lines[0] == expected


@pytest.mark.slow
@pytest.mark.parametrize(
    "project_name",
    [
        "yara",  # make
        "cppcheck",  # cmake
        "example",
    ],
)
def test_build_command_export_commands(project_name, tmp_path):
    checkout = CheckoutCommand()
    checkout(f"{project_name} 1 --target {str(tmp_path)}".split())
    # FIXME: Due to Github Action bug, it creates a directory owned by root even if user option is specified.
    for directory in filter(Path.is_dir, tmp_path.rglob("*")):
        directory.chmod(0o777)

    build = BuildCommand()
    build(
        f"{str(tmp_path / project_name / 'fixed-1')} --export={str(tmp_path)}".split()
    )

    assert (tmp_path / "compile_commands.json").exists()


@pytest.mark.skip("Rebuild image is currently not used(deprecated.)")
def test_build_command_rebuild_image(create_build, meta_json, capsys):
    build = create_build(meta_json, {"rebuild_image": True})
    # build yara image
    build([])
    _, _ = capsys.readouterr()
    with capsys.disabled():
        print("\nTesting test_build_command_rebuild_image")

    # Build yara image again
    # Try to rebuild the same image 5 times
    # related to: https://github.com/Suresoft-GLaDOS/defects4cpp/pull/67
    rebuild_attempts = 5
    for attempt in range(1, rebuild_attempts + 1):
        with capsys.disabled():
            print(f"  Rebuild attempt {attempt}/{rebuild_attempts}")
        try:
            build([])
            stdout, _ = capsys.readouterr()
        except docker.errors.APIError:
            # Sleep longer and longer...
            time.sleep(attempt)
            continue
        else:
            assert all(
                x in stdout
                for x in [
                    "start building",
                    "hschoe/defects4cpp-ubuntu:test_build_command_rebuild_image",
                    "done",
                ]
            )
            break
    else:
        assert False, "Failed to rebuild image"
