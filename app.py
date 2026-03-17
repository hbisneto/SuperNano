import sys
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea, ListView, ListItem, Header, Footer, Input
from textual.containers import Horizontal, Vertical
from pygments.lexers import guess_lexer

TEXT = """\
SuperNano Editor

Welcome! This editor works like a simple system text editor.

Keyboard shortcuts:

CTRL + S  → Save file
CTRL + O  → Open file
CTRL + Q  → Quit editor
CTRL + F  → Search text

Start typing to edit the document.
"""

class SuperNano(App):

    CSS_PATH = "style.tcss"

    BINDINGS = [
        ("ctrl+s", "save", "Save"),
        ("ctrl+q", "quit", "Quit"),
        ("ctrl+o", "open_path", "Open"),
    ]

    def __init__(self):
        super().__init__()
        self.current_path = None
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
        # self.editor = TextArea("", id="editor", language="python")
        self.editor = TextArea.code_editor(
            "",
            id="editor",
            language="python"
        )
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

    def detect_language_from_content(self):
        editor = self.query_one("#editor", TextArea)
        try:
            lexer = guess_lexer(editor.text)
            # 🔥 pega o primeiro alias válido
            if lexer.aliases:
                editor.language = lexer.aliases[0]
            else:
                editor.language = None
        except Exception:
            editor.language = None
        editor.refresh()

    def on_key(self, event):
        if event.key == "escape":
            input_widget = self.query_one("#path_input", Input)
            if input_widget.display:
                input_widget.display = False
                self.query_one("#editor", TextArea).focus()

    def on_mount(self):
        if self.current_path and self.current_path.exists():
            self.load_file(str(self.current_path.absolute()))

    def on_list_view_selected(self, event: ListView.Selected):
        if hasattr(event.item, "path"):
            self.load_file(str(event.item.path))

    def load_file(self, path_str):
        try:
            path = Path(path_str)
            editor = self.query_one("#editor", TextArea)
            editor.text = path.read_text(encoding="utf-8")
            self.set_language(path)
            self.current_path = path
            # self.status.update(f"Current File: {path.name}")
            self.set_language(path)
            self.status.update(
                f"{path.name} | {editor.language} | UTF-8"
            )
        except Exception as e:
            self.status.update(f"Error when opening: {e}")

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

    def action_save(self):
        if self.current_path:
            try:
                editor = self.query_one("#editor", TextArea)
                self.current_path.write_text(
                    editor.text,
                    encoding="utf-8"
                )
                self.status.update(f"SAVED: {self.current_path.name}")
            except Exception as e:
                self.status.update(f"Error when saving: {e}")
        else:
            self.status.update("Error: There's not opened file to save!")

    def action_open_path(self):
        input_widget = self.query_one("#path_input", Input)
        input_widget.display = True
        input_widget.value = ""
        input_widget.focus()
        self.status.update("Enter file path and press Enter")

    def on_input_submitted(self, event: Input.Submitted):
        path = Path(event.value).expanduser()
        if path.exists():
            self.load_file(str(path))
            self.query_one("#editor", TextArea).focus()
        else:
            self.status.update("File not found")
        event.input.display = False

if __name__ == "__main__":
    SuperNano().run()