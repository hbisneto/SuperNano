# search/strategies.py

from abc import ABC, abstractmethod
from search.models import SearchQuery

class SearchStrategy(ABC):
    @abstractmethod
    def find(self, text: str, query: SearchQuery) -> list[int]:
        pass

class LiteralSearchStrategy(SearchStrategy):
    def find(self, text: str, query: SearchQuery) -> list[int]:
        term = query.term

        if not term:
            return []

        if not query.case_sensitive:
            text = text.lower()
            term = term.lower()

        matches = []
        start = 0

        while True:
            idx = text.find(term, start)
            if idx == -1:
                break

            matches.append(idx)
            start = idx + len(term)

        return matches