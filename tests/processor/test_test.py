import defects4cpp.processor
import defects4cpp.taxonomy


def test_checkout_modify_lua_script():
    cmd = defects4cpp.processor.TestCommand()
    t = defects4cpp.taxonomy.Taxonomy()
    yara = t["yara"]

    command = cmd._select_index(yara.defects[0], 1)
    assert "return 1" in command

    command = cmd._select_index(yara.defects[0], 3)
    assert "return 3" in command
