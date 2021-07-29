import errors
import processor
import taxonomy
from processor.test import _make_filter_command


def test_checkout_modify_lua_script():
    t = taxonomy.Taxonomy()
    yara = t["yara"]

    filter_command = _make_filter_command(yara.defects[0])
    assert "return 1" in filter_command(1)
    assert "return 3" in filter_command(3)


def test_validate_case(dummy_config):
    d = dummy_config("test_validate_case")
    cmd = processor.TestCommand()
    default_cmds = f"{str(d)} --case".split()

    expr = "1,2,5,9"
    args = cmd.parser.parse_args([*default_cmds, expr])
    assert args.case == ({1, 2, 5, 9}, set())

    expr = "1-5,5-9"
    args = cmd.parser.parse_args([*default_cmds, expr])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, set())

    expr = "1-5,5-9:"
    args = cmd.parser.parse_args([*default_cmds, expr])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, set())

    expr = "1-5,5-9:1"
    args = cmd.parser.parse_args([*default_cmds, expr])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, {1})

    expr = "1-5,5-9:1,2"
    args = cmd.parser.parse_args([*default_cmds, expr])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, {1, 2})

    expr = "1-5,5-9:1-3"
    args = cmd.parser.parse_args([*default_cmds, expr])
    assert args.case == ({1, 2, 3, 4, 5, 6, 7, 8, 9}, {1, 2, 3})

    expr = "4-8:1-3,9"
    args = cmd.parser.parse_args([*default_cmds, expr])
    assert args.case == ({4, 5, 6, 7, 8}, {1, 2, 3, 9})

    expr = ":1-3,9"
    args = cmd.parser.parse_args([*default_cmds, expr])
    assert args.case == (set(), {1, 2, 3, 9})


def test_invalid_case_expression(dummy_config):
    d = dummy_config("test_validate_case")
    cmd = processor.TestCommand()
    project_name = "yara"
    index = 1
    default_cmds = f"{str(d)} --case".split()

    t = taxonomy.Taxonomy()
    project = t[project_name]
    cases = project.defects[index].cases

    expr = f"{cases+1}"
    try:
        cmd.parser.parse_args([*default_cmds, expr])
    except errors.DppInvalidCaseExpressionError:
        assert True
    else:
        assert False


def test_no_case_is_provided(dummy_config):
    d = dummy_config("test_validate_case")
    cmd = processor.TestCommand()
    default_cmds = f"{str(d)}".split()

    args = cmd.parser.parse_args(default_cmds)
    metadata = args.metadata
    index = args.worktree.index
    selected_defect: taxonomy.Defect = metadata.defects[index - 1]

    docker_cmd = cmd.run(default_cmds)
    assert len(list(docker_cmd.scripts)) == selected_defect.cases


def test_exclude_only(dummy_config):
    d = dummy_config("test_validate_case")
    cmd = processor.TestCommand()
    default_cmds = f"{str(d)} --case :1-100".split()

    args = cmd.parser.parse_args(default_cmds)
    metadata = args.metadata
    index = args.worktree.index
    selected_defect: taxonomy.Defect = metadata.defects[index - 1]

    docker_cmd = cmd.run(default_cmds)
    assert len(list(docker_cmd.scripts)) == (selected_defect.cases - 100)
