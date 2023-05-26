import pytest
from errors.internal import DppMetaDataInitKeyError, DppMetaDataInitTypeError

from bugscpp.config import config, env
from bugscpp.taxonomy import Taxonomy


def test_metadata_variables_should_be_replaced():
    t = Taxonomy()
    metadata = t["yara"]

    common = metadata.common
    line = common.build_command[0].lines[-1]
    assert line == f"make -j{env.DPP_PARALLEL_BUILD}"

    common_capture = metadata.common_capture
    line = common_capture.build_command[0].lines[-1]
    assert line == f"{env.DPP_COMPILATION_DB_TOOL} make -j{env.DPP_PARALLEL_BUILD}"


def test_metadata_setting_compilation_db_tool_should_remove_cmake_export_macro(
    keep_config,
):
    t = Taxonomy()
    metadata = t["cppcheck"]  # cmake project
    assert any(
        "-DCMAKE_EXPORT_COMPILE_COMMANDS=1" in line
        for line in metadata.common_capture.build_command[0].lines
    )

    config.DPP_CMAKE_COMPILATION_DB_TOOL = "foo"
    assert not any(
        "-DCMAKE_EXPORT_COMPILE_COMMANDS=1" in line
        for line in metadata.common_capture.build_command[0].lines
    )


@pytest.mark.parametrize("attr_name", ["DPP_BUILD_PRE_STEPS", "DPP_BUILD_POST_STEPS"])
def test_metadata_build_pre_steps_with_missing_key_should_throw(keep_config, attr_name):
    setattr(config, attr_name, [{"typo": "docker", "lines": ["echo hello, world!"]}])
    t = Taxonomy()
    metadata = t["yara"]
    with pytest.raises(DppMetaDataInitKeyError):
        metadata.common.build_command[0]


@pytest.mark.parametrize("attr_name", ["DPP_BUILD_PRE_STEPS", "DPP_BUILD_POST_STEPS"])
def test_metadata_build_steps_with_invalid_value_should_throw(keep_config, attr_name):
    setattr(config, attr_name, [{"type": "foo", "lines": ["echo hello, world!"]}])
    t = Taxonomy()
    metadata = t["yara"]
    with pytest.raises(DppMetaDataInitTypeError):
        metadata.common.build_command[0]


@pytest.mark.parametrize("command_type", ["docker", "script"])
def test_metadata_docker_build_steps_should_be_inserted(keep_config, command_type):
    config.DPP_BUILD_PRE_STEPS = [
        {"type": command_type, "lines": ["echo pre hello, world!"]}
    ]
    config.DPP_BUILD_POST_STEPS = [
        {"type": command_type, "lines": ["echo post hello, world!"]}
    ]

    t = Taxonomy()
    metadata = t["yara"]
    for c in [metadata.common, metadata.common_capture]:
        assert c.build_command[0].type.lower() == command_type
        assert c.build_command[0].lines[0] == "echo pre hello, world!"
        assert c.build_command[-1].type.lower() == command_type
        assert c.build_command[-1].lines[0] == "echo post hello, world!"

        assert c.build_coverage_command[0].type.lower() == command_type
        assert c.build_coverage_command[0].lines[0] == "echo pre hello, world!"
        assert c.build_coverage_command[-1].type.lower() == command_type
        assert c.build_coverage_command[-1].lines[0] == "echo post hello, world!"

        # test-command must not be touched.
        assert c.test_command[0].lines[0] != "echo pre hello, world!"
        assert c.test_coverage_command[0].lines[0] != "echo pre hello, world!"
        assert c.test_command[-1].lines[0] != "echo post hello, world!"
        assert c.test_coverage_command[-1].lines[0] != "echo post hello, world!"


def test_metadata_variables_should_be_replaced():
    t = Taxonomy()
    metadata = t["yara"]

    common = metadata.common
    line = common.build_command[0].lines[-1]
    assert line == f"make -j{env.DPP_PARALLEL_BUILD}"

    common_capture = metadata.common_capture
    line = common_capture.build_command[0].lines[-1]
    assert line == f"{env.DPP_COMPILATION_DB_TOOL} make -j{env.DPP_PARALLEL_BUILD}"


def test_extra_tests():
    t = Taxonomy()
    assert t["yara"].defects[0].extra_tests is not None
    assert t["yara"].defects[0].extra_tests == []
    assert t["libtiff"].defects[0].extra_tests is not None
    assert len(t["libtiff"].defects[0].extra_tests) == 1
