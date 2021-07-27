from taxonomy import Taxonomy


def test_taxonomy():
    t = Taxonomy()
    taxonomy_size = 2
    assert len(t) == taxonomy_size
