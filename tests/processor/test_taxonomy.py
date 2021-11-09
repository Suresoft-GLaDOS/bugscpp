from taxonomy import Taxonomy
from config import env


def test_taxonomy():
    t = Taxonomy()
    taxonomy_size = 13
    assert len(t) == taxonomy_size


def test_metadata():
    t = Taxonomy()
    metadata = t["yara"]

    common = metadata.common
    line = common.build_command.lines[-1]
    assert line == f"make -j{env.DPP_PARALLEL_BUILD}"

    common_capture = metadata.common_capture
    line = common_capture.build_command.lines[-1]
    assert line == f"{env.DPP_COMPILATION_DB_TOOL} make -j{env.DPP_PARALLEL_BUILD}"
