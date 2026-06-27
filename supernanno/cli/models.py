# cli/models.py

from dataclasses import dataclass

@dataclass
class CLIArgs:
    backup: bool = False
    backup_dir: str | None = None
    column: int = 0
    file: str | None = None
    help: bool = False
    invalid_arg: str | None = None
    line: int | None = None
    search: str | None = None
    view_mode: bool = False
    version: bool = False
    show_line_numbers: bool = False # Implement