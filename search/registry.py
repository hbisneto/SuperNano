# search/registry.py

from search.strategies import LiteralSearchStrategy

class SearchRegistry:
    def __init__(self):
        self._strategies = {
            "literal": LiteralSearchStrategy()
        }

    def register(self, name: str, strategy):
        self._strategies[name] = strategy

    def get(self, name: str = "literal"):
        return self._strategies[name]