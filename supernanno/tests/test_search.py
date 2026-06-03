# tests/test_search.py

from supernanno.search.engine import SearchEngine
from supernanno.search.models import SearchQuery

def test_literal_search_case_insensitive():
    engine = SearchEngine()
    text = "Hello World hello again"
    result = engine.search(text, SearchQuery(term="hello"))

    assert len(result.matches) == 2
    assert result.matches == [0, 12]

def test_literal_search_case_sensitive():
    engine = SearchEngine()
    text = "Hello World hello"
    result = engine.search(text, SearchQuery(term="Hello", case_sensitive=True))

    assert result.matches == [0]