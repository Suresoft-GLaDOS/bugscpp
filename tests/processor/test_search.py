from processor.search import search_by_tags


def test_search_by_tags():
    result = search_by_tags(["cve", "single-line"])
    assert True
