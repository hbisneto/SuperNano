# search/controller.py

from ..search.engine import SearchEngine
from ..search.models import SearchQuery, SearchResult

class SearchController:
    def __init__(self):
        self.engine = SearchEngine()

    def search(self, text: str, term: str) -> SearchResult:
        if not term.strip():
            return SearchResult()
        return self.engine.search(text, SearchQuery(term=term))