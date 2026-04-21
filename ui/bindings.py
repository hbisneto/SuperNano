# ui/bindings.py

CSS_FILE = "style.tcss"

BINDINGS = [
    ("ctrl+b", "show_hide_sidebar", "Show/Hide Sidebar"),
    ("ctrl+n", "new_file", "New"),
    ("ctrl+o", "open_path", "Open"),
    ("ctrl+s", "save", "Save"),
    ("ctrl+r", "read_file", "Read File"),
    ("ctrl+f", "search", "Search"),
    ("ctrl+q", "quit", "Quit"),
    ("f1", "show_settings", "Settings"),
]

SETTINGS_BINDINGS = [
    ("escape", "dismiss", "Close"),
    ("ctrl+s", "save", "Save Settings"),
]

WELCOME = """\
# SuperNanno 0.4.0

Welcome! This editor works like a simple system text editor.

Keyboard shortcuts:

CTRL + B: Show/Hide Sidebar
CTRL + N: New File
CTRL + O: Open File
CTRL + S: Save File
CTRL + R: Read file
CTRL + F: Search Text
CTRL + Q: Quit Editor
F1: Settings

Start typing to edit the document.
"""

IS_WELCOME_TEXT = WELCOME.strip()