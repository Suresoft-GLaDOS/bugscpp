from config import env
from taxonomy import Taxonomy


def test_taxonomy():
    t = Taxonomy()
    taxonomy_size = 12
    assert len(t) == taxonomy_size


def test_metadata():
    t = Taxonomy()
    metadata = t["yara"]

    common = metadata.common
    line = common.build_command[0].lines[-1]
    assert line == f"make -j{env.DPP_PARALLEL_BUILD}"

    common_capture = metadata.common_capture
    line = common_capture.build_command[0].lines[-1]
    assert line == f"{env.DPP_COMPILATION_DB_TOOL} make -j{env.DPP_PARALLEL_BUILD}"
