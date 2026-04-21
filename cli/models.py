# cli/models.py

from dataclasses import dataclass

@dataclass
class CLIArgs:
    file: str | None = None
    line: int | None = None
    column: int = 0
    search: str | None = None

    view_mode: bool = False
    backup: bool = False
    backup_dir: str | None = None

    help: bool = False
    version: bool = False

    invalid_arg: str | None = None