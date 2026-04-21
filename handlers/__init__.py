# handlers/__init__.py

from .file import (
    new,
    open as open_file,
    load,
    read,
    save,
    save_as,
)

from .quit import execute as quit

__all__ = ["new", "open_file", "load", "read", "save", "save_as", "quit"]