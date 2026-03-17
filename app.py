import sys
from datetime import datetime
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea, ListView, ListItem, Header, Footer, Input
from textual.containers import Horizontal, Vertical
from pygments.lexers import guess_lexer

TEXT = """\
# SuperNano Editor

Welcome! This editor works like a simple system text editor.

Keyboard shortcuts:

CTRL + F  → Search text
CTRL + O  → Open file
CTRL + N  → New file
CTRL + Q  → Quit editor
CTRL + S  → Save file

Start typing to edit the document.
"""

class SuperNano(App):

    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("ctrl+f", "search", "Search"),
        ("ctrl+o", "open_path", "Open"),
        ("ctrl+n", "new_file", "New"),
        ("ctrl+q", "quit", "Quit"), 
        ("ctrl+s", "save", "Save"),
    ]

    def __init__(self):
        super().__init__()
        self.current_path = None
        self.input_mode = None
        self.is_dirty = False
        self.temp_file = None
        self._loading = False
        self.confirm_action = None
        self._confirm_quit = False
        self._original_text = ""
        if len(sys.argv) > 1:
            self.current_path = Path(sys.argv[1])

    def compose(self) -> ComposeResult:
        yield Header()
        files = []

        for f in Path(".").iterdir():
            if f.is_file():
                item = ListItem(Static(f.name))
                item.path = f
                files.append(item)

        self.file_list = ListView(*files, id="files")
        self.path_input = Input(
            placeholder="Enter file path: ~/Documents/file.txt",
            id="path_input"
        )
        self.editor = TextArea.code_editor(
            "",
            id="editor",
            language="markdown"
        )
        self.editor.text = TEXT

        self.status = Static("SuperNano Ready", id="status")
        self.path_input.display = False

        yield Horizontal(
            Vertical(
                Static("FILES", classes="title"),
                self.file_list,
                id="sidebar"
            ),
            Vertical(
                self.path_input,
                self.editor,
                self.status,
                id="main"
            )
        )
        
        yield self.path_input
        yield Footer()

    ###==================== ACTIONS ====================###
    
    def action_save(self):
        if self.current_path:
            try:
                editor = self.query_one("#editor", TextArea)
                self.current_path.write_text(editor.text, encoding="utf-8")
                self.status.update(f"SAVED: {self.current_path.name}")
                self.is_dirty = False
                self._confirm_quit = False
                self.refresh_file_list()
            except Exception as e:
                self.status.update(f"Error when saving: {e}")
        else:
            self.prompt_save_as()

    def action_search(self):
        input_widget = self.query_one("#path_input", Input)
        input_widget.display = True
        input_widget.placeholder = "Search..."
        input_widget.focus()
        self.input_mode = "search"

    def action_open_path(self):
        input_widget = self.query_one("#path_input", Input)
        input_widget.display = True
        input_widget.value = ""
        input_widget.focus()
        self.input_mode = "open"
        self.status.update("Enter file path and press Enter")

    def action_new_file(self):
        editor = self.query_one("#editor", TextArea)
        self._loading = True
        editor.text = ""
        self._original_text = ""
        self._loading = False
        self.is_dirty = False

        editor.language = None
        self.current_path = None

        self.status.update("New file (unsaved)")

    def action_quit(self):
        if self.is_dirty:
            if self.confirm_action:
                self.is_dirty = False
                action = self.confirm_action
                self.confirm_action = None
                action()
                self.status.update("Changes discarded")
            elif getattr(self, "_confirm_quit", False):
                self.exit()
            else:
                self._confirm_quit = True
                self.status.update("Unsaved changes! Press CTRL+Q again to exit.")
        else:
            self.exit()

    ###==================== ACTIONS ====================###

    ###==================== ON EVENT ====================###
    
    def on_input_submitted(self, event: Input.Submitted):
        value = event.value

        if self.input_mode == "search":
            editor = self.query_one("#editor", TextArea)
            index = editor.text.find(value)
            if index != -1:
                editor.cursor_location = editor.document.get_location_from_index(index)
                self.status.update(f"Found: {value}")
            else:
                self.status.update("Not found")

        elif self.input_mode == "save":
            path = Path(value).expanduser()
            try:
                editor = self.query_one("#editor", TextArea)
                path.write_text(editor.text, encoding="utf-8")
                self.current_path = path
                self.is_dirty = False
                self.status.update(f"SAVED: {path}")
                self.refresh_file_list()
            except Exception as e:
                self.status.update(f"Error saving: {e}")

        else:  # open
            path = Path(value).expanduser()
            if path.exists():
                self.load_file(str(path))
                self.query_one("#editor", TextArea).focus()
            else:
                self.status.update("File not found")

        self.input_mode = None
        event.input.display = False

    def on_key(self, event):
        if event.key == "escape":
            input_widget = self.query_one("#path_input", Input)
            if input_widget.display:
                input_widget.display = False
                self.query_one("#editor", TextArea).focus()

    def on_list_view_selected(self, event: ListView.Selected):
        if not hasattr(event.item, "path"):
            return

        if self.is_dirty:
            if self.confirm_action:
                action = self.confirm_action
                self.confirm_action = None
                self.is_dirty = False
                action()
                return

            self.confirm_action = lambda: self.load_file(str(event.item.path))
            self.status.update("Click again to discard changes")
            return
        self.load_file(str(event.item.path))
        
    def on_mount(self):
        if self.current_path and self.current_path.exists():
            self.load_file(str(self.current_path.absolute()))
    
    def on_text_area_changed(self, event):
        editor = self.query_one("#editor", TextArea)
        self.is_dirty = (editor.text != self._original_text)
        dirty_flag = "*" if self.is_dirty else ""
        if self.current_path == None:
            self.status.update(f"SuperNanno | {editor.language} | UTF-8")
        else:    
            self.status.update(f"{self.current_path}{dirty_flag} | {editor.language} | UTF-8")

    ###==================== ON EVENT ====================###

    def detect_language_from_content(self):
        editor = self.query_one("#editor", TextArea)
        try:
            lexer = guess_lexer(editor.text)
            if lexer.aliases:
                editor.language = lexer.aliases[0]
            else:
                editor.language = None
        except Exception:
            editor.language = None
        editor.refresh()

    def load_file(self, path_str):
        try:
            path = Path(path_str)
            editor = self.query_one("#editor", TextArea)
            self._loading = True
            editor.text = path.read_text(encoding="utf-8")
            self._original_text = editor.text
            self.set_language(path)
            self.current_path = path
            self.is_dirty = False
            self._loading = False
            self.status.update(f"{path} | {editor.language} | UTF-8")

        except Exception as e:
            self.status.update(f"Error when opening: {e}")

    def prompt_save_as(self):
        input_widget = self.query_one("#path_input", Input)
        input_widget.display = True
        input_widget.placeholder = "Save as: ./file.txt"
        input_widget.value = "./"
        input_widget.focus()

        self.input_mode = "save"
        self.status.update("Enter path to save file")

    def refresh_file_list(self):
        self.file_list.clear()

        for f in Path(".").iterdir():
            if f.is_file():
                item = ListItem(Static(f.name))
                item.path = f
                self.file_list.append(item)

    def set_language(self, path: Path):
        ext = path.suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".cs": "csharp",
            ".json": "json",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
            ".sh": "bash",
            ".c": "c",
            ".cpp": "cpp"
        }

        editor = self.query_one("#editor", TextArea)
        # 1️⃣ tenta pela extensão
        lang = language_map.get(ext)
        if lang:
            editor.language = lang
        else:
            # 2️⃣ fallback pelo conteúdo
            try:
                lexer = guess_lexer(editor.text)
                editor.language = lexer.aliases[0] if lexer.aliases else None
            except Exception:
                editor.language = None
        editor.refresh()

if __name__ == "__main__":
    SuperNano().run()