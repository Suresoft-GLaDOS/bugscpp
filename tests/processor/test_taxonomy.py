import pytest
from errors.internal import DppMetaDataInitKeyError, DppMetaDataInitTypeError

from defects4cpp.config import config, env
from defects4cpp.taxonomy import Taxonomy


def test_taxonomy():
    t = Taxonomy()
    taxonomy_size = 12
    assert len(t) == taxonomy_size


def test_metadata_variables_should_be_replaced():
    t = Taxonomy()
    metadata = t["yara"]

    common = metadata.common
    line = common.build_command[0].lines[-1]
    assert line == f"make -j{env.DPP_PARALLEL_BUILD}"

    common_capture = metadata.common_capture
    line = common_capture.build_command[0].lines[-1]
    assert line == f"{env.DPP_COMPILATION_DB_TOOL} make -j{env.DPP_PARALLEL_BUILD}"


def test_metadata_build_pre_steps_with_missing_key_should_throw(keep_config):
    config.DPP_BUILD_PRE_STEPS = [{"typo": "docker", "lines": ["echo hello, world!"]}]
    t = Taxonomy()
    metadata = t["yara"]
    with pytest.raises(DppMetaDataInitKeyError):
        metadata.common.build_command[0]


def test_metadata_build_pre_steps_with_invalid_value_should_throw(keep_config):
    config.DPP_BUILD_PRE_STEPS = [{"type": "foo", "lines": ["echo hello, world!"]}]
    t = Taxonomy()
    metadata = t["yara"]
    with pytest.raises(DppMetaDataInitTypeError):
        metadata.common.build_command[0]


@pytest.mark.parametrize("command_type", ["docker", "script"])
def test_metadata_docker_build_pre_steps_should_be_inserted(keep_config, command_type):
    config.DPP_BUILD_PRE_STEPS = [
        {"type": command_type, "lines": ["echo hello, world!"]}
    ]
    t = Taxonomy()
    metadata = t["yara"]
    for c in [metadata.common, metadata.common_capture]:
        assert c.build_command[0].type.lower() == command_type
        assert c.build_command[0].lines[0] == "echo hello, world!"

        assert c.build_coverage_command[0].type.lower() == command_type
        assert c.build_coverage_command[0].lines[0] == "echo hello, world!"

        # test-command must not be touched.
        assert c.test_command[0].lines[0] != "echo hello, world!"
        assert c.test_coverage_command[0].lines[0] != "echo hello, world!"
