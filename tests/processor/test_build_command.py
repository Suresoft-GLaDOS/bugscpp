from pathlib import Path

import pytest

from defects4cpp.command import BuildCommand, CheckoutCommand
from defects4cpp.config import config


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
    meta_json["common"]["build"]["command"]["lines"] = [
        "@DPP_COMPILATION_DB_TOOL@ command"
    ]
    meta_json["common"]["build-coverage"]["command"]["lines"] = [
        "coverage_command @DPP_COMPILATION_DB_TOOL@"
    ]
    build = create_build(meta_json, {"coverage": coverage, "export": export})
    generator = build.create_script_generator(build.parser.parse_args([]))

    for script in generator.create():
        assert len(script.lines) == 1
        assert script.lines[0] == expected


@pytest.mark.parametrize(
    "project_name",
    [
        "yara",  # make
        "cppcheck",  # cmake
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
        f"{str(tmp_path / project_name / 'fixed#1')} --export={str(tmp_path)}".split()
    )

    assert (tmp_path / "compile_commands.json").exists()
