import pytest
from errors import DppNoSuchTagError
from processor.search import SearchCommand, search_by_tags
from taxonomy import Taxonomy


@pytest.mark.parametrize(
    "tags", [["cve", "single-line"], ["logical-error", "multi-line", "modified", "cve"]]
)
def test_search_by_tags(tags):
    result = search_by_tags(tags)
    taxonomy = Taxonomy()
    for name in taxonomy:
        if name == "example":
            continue
        for defect in taxonomy[name].defects:
            if all(tag.lower() in defect.tags for tag in tags):
                assert f"{name}-{defect.id}" in result


def test_search_by_tags_should_be_empty():
    assert search_by_tags(["no-such-tag"]) == []


def test_search_command_should_raise_no_such_tag_error():
    with pytest.raises(DppNoSuchTagError):
        SearchCommand()(["no-such-tag"])


def test_search_command_withouth_any_args(capsys):
    with pytest.raises(SystemExit):
        SearchCommand()([])
    captured = capsys.readouterr()
    assert "usage: \nbugcpp.py search TAGS" in captured.err
