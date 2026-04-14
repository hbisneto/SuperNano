# cli/models.py

from dataclasses import dataclass
from pathlib import Path

@dataclass
class CLIArgs:
    file: str | None = None
    line: int | None = None
    column: int = 0
    search: str | None = None
    view_mode: bool = False

    help: bool = False
    version: bool = False