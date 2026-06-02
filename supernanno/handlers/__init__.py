# handlers/__init__.py

from .file import (
    new,
    open as open_file,
    load,
    read,
    save,
    save_as
)

from .toggle_sidebar import execute as toggle_sidebar
from .quit import execute as quit

__all__ = ["new", "open_file", "load", "read", "save", "save_as", "toggle_sidebar", "quit"]