# search/models.py

from dataclasses import dataclass, field

@dataclass
class SearchQuery:
    term: str
    case_sensitive: bool = False
    regex: bool = False
    whole_word: bool = False

@dataclass
class SearchResult:
    matches: list[int] = field(default_factory=list)
    current_index: int = 0

    @property
    def has_matches(self) -> bool:
        return bool(self.matches)