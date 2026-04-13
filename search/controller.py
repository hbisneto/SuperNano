# search/controller.py

from search.engine import SearchEngine
from search.models import SearchQuery, SearchResult

class SearchController:
    def __init__(self):
        self.engine = SearchEngine()

    def search(self, ctx, term: str) -> SearchResult:
        result = self.find(ctx.editor.text, term)

        if not result.has_matches:
            ctx.status.set(f"Not Found: '{term}'")
            return result

        self.go_to_match(ctx, result, 0, term)
        return result

    def find(self, text: str, term: str) -> SearchResult:
        return self.engine.search(text, SearchQuery(term=term))

    def go_to_match(self, ctx, result: SearchResult, index: int, term: str):
        if not result.has_matches or index < 0 or index >= len(result.matches):
            return

        idx = result.matches[index]
        editor = ctx.editor

        start = editor.document.get_location_from_index(idx)
        end   = editor.document.get_location_from_index(idx + len(term))

        editor.cursor_location = start
        editor.selection = (start, end)

        ctx.status.set(f"Match {index + 1}/{len(result.matches)}: '{term}'")