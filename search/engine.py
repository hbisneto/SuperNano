# search/engine.py

from search.models import SearchQuery, SearchResult
from search.registry import SearchRegistry

class SearchEngine:
    def __init__(self, registry: SearchRegistry | None = None):
        self.registry = registry or SearchRegistry()

    def search(self, text: str, query: SearchQuery, strategy="literal") -> SearchResult:
        finder = self.registry.get(strategy)
        matches = finder.find(text, query)
        return SearchResult(matches=matches)