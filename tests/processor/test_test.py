import defects4cpp.processor
import defects4cpp.taxonomy


def test_checkout_modify_lua_script():
    cmd = defects4cpp.processor.TestCommand()
    t = defects4cpp.taxonomy.Taxonomy()
    yara = t["yara"]

    filter_command = cmd._make_filter_command(yara.defects[0])
    assert "return 1" in filter_command(1)
    assert "return 3" in filter_command(3)


def test_validate_case():
    cmd = defects4cpp.processor.TestCommand()
    default_cmds = ["--project", "yara", "--no", "1", "--case"]

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


def test_no_case_is_provided():
    cmd = defects4cpp.processor.TestCommand()
    default_cmds = ["--project", "yara", "--no", "1"]

    args = cmd.parser.parse_args([*default_cmds])
    metadata = args.metadata
    index = args.index
    selected_defect: defects4cpp.taxonomy.Defect = metadata.defects[index - 1]

    docker_cmd = cmd.run(default_cmds)
    assert len(list(docker_cmd.commands)) == (selected_defect.cases * 2)


def test_exclude_only():
    cmd = defects4cpp.processor.TestCommand()
    default_cmds = ["--project", "yara", "--no", "1", "--case", ":1-100"]

    args = cmd.parser.parse_args([*default_cmds])
    metadata = args.metadata
    index = args.index
    selected_defect: defects4cpp.taxonomy.Defect = metadata.defects[index - 1]

    docker_cmd = cmd.run(default_cmds)
    assert len(list(docker_cmd.commands)) == (selected_defect.cases - 100) * 2
