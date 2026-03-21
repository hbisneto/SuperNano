import asyncio
import json
import os
import sys
from pathlib import Path
from textual.app import App, ComposeResult
from textual.widgets import Static, TextArea, ListView, ListItem, Header, Footer, Input
from textual.containers import Horizontal, Vertical
from pygments.lexers import guess_lexer

from commands import save
from services.app_context import AppContext

TEXT = """\
# SuperNanno 0.1.5

Welcome! This editor works like a simple system text editor.

Keyboard shortcuts:

CTRL + F  → Search text
CTRL + O  → Open file
CTRL + N  → New file
CTRL + Q  → Quit editor
CTRL + S  → Save file

Start typing to edit the document.
"""

class SuperNanno(App):
    CSS_PATH = "style.tcss"
    BINDINGS = [
        ("ctrl+f", "search", "Search"),
        ("ctrl+o", "open_path", "Open"),
        ("ctrl+n", "new_file", "New"),
        ("ctrl+u", "quit", "Quit"),
        ("ctrl+s", "save", "Save"),
        ("ctrl+r", "read_file", "Read File"),
    ]

    def __init__(self):
        super().__init__()
        self.input_mode = None
        self.temp_file = None
        self._loading = False
        self.confirm_action = None
        self._confirm_quit = False
        self._original_text = ""
        self._status_locked = False
        self.ctx = AppContext(self)
        if len(sys.argv) > 1:
            self.ctx.current_path = Path(sys.argv[1])

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

        self.status = Static("SuperNanno Ready", id="status")
        self.path_input.display = False

        yield Horizontal(
            Vertical(
                Static("FILES", classes="title"),
                self.file_list,
                id="sidebar"
            ),
            Vertical(
                self.editor,
                self.path_input,
                self.status,
                id="main"
            )
        )
        
        yield Footer()

    ###==================== ACTIONS ====================###
    
    def action_save(self):
        save.execute(self.ctx)

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
        self.set_status(
            text=f"[!]: Enter file path and press Enter",
            delay=0
        )

    def action_new_file(self):
        editor = self.get_editor()
        self._loading = True
        editor.text = ""
        self._original_text = ""
        self._loading = False
        self.ctx.is_dirty = False
        editor.language = None
        self.ctx.current_path = None
        editor.focus()
        self.status.update("New file (unsaved)")

    def action_quit(self):
        if self.ctx.is_dirty:
            if self.confirm_action:
                self.ctx.is_dirty = False ## Mantive esse
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

    def action_read_file(self):
        input_widget = self.query_one("#path_input", Input)
        input_widget.display = True
        input_widget.placeholder = "Enter file path..."
        input_widget.value = ""
        input_widget.focus()
        self.input_mode = "read_file"

    ###==================== ACTIONS ====================###

    ###==================== ON EVENT ====================###
    
    def on_input_submitted(self, event: Input.Submitted):
        value = event.value
        # editor = self.get_editor()

        if self.input_mode == "read_file":
            path = Path(event.value).expanduser()
            if not path.exists():
                self.set_status(f"File not found: {path}", delay=3, status_type="error")
                return
            if path.is_dir():
                self.set_status("Cannot read a directory", delay=3, status_type="warning")
                return
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
                editor = self.get_editor()
                text = editor.text         
                if editor.selection:
                    start, end = editor.selection
                    start_index = editor.document.get_index_from_location(start)
                    end_index = editor.document.get_index_from_location(end)
                    if start_index > end_index:
                        start_index, end_index = end_index, start_index
                    before = text[:start_index]
                    after = text[end_index:]
                    new_text = before + content + after
                    new_index = start_index + len(content)
                else:
                    cursor = editor.cursor_location
                    index = editor.document.get_index_from_location(cursor)
                    before = text[:index]
                    after = text[index:]
                    new_text = before + content + after
                    new_index = index + len(content)
                editor.text = new_text
                new_location = editor.document.get_location_from_index(new_index)
                editor.cursor_location = new_location
                self.set_status(f"(Inserted): {path}", delay=3, status_type="success")
            except Exception as e:
                self.set_status(f"(Error): {e}", delay=3, status_type="error")
            self.input_mode = None
            event.input.display = False
            return

        if self.input_mode == "search":
            editor = self.get_editor()
            index = editor.text.find(value)
            if index != -1:
                editor.cursor_location = editor.document.get_location_from_index(index)
                self.status.update(f"Found: {value}")
            else:
                self.status.update("Not found")

        elif self.input_mode == "save":
            path = Path(value).expanduser()
            try:
                editor = self.get_editor()
                path.write_text(editor.text, encoding="utf-8")
                self.ctx.current_path = path
                self.ctx.is_dirty = False
                self.set_status(
                    text=f"(Saved): Your file is saved: {self.ctx.current_path.name}",
                    delay=3,
                    next_text=self.get_default_status(),
                )
                self.refresh_file_list()
            except Exception as e:
                self.set_status(
                    text=f"(Error): Could not save file: {e}",
                    delay=5,
                    next_text=f"SuperNanno | Ready! | UTF-8",
                    status_type="error"
                )
        else:
            path = Path(value).expanduser()
            if path.exists():
                self.load_file(str(path))
                self.get_editor().focus()
            else:
                self.status.update("File not found")

        self.input_mode = None
        event.input.display = False

    def on_key(self, event):
        if event.key == "escape":
            input_widget = self.query_one("#path_input", Input)
            if input_widget.display:
                input_widget.display = False
                self.get_editor().focus()

    def on_list_view_selected(self, event: ListView.Selected):
        self.status.remove_class("success")
        self.status.remove_class("info")
        self.status.remove_class("warning")
        self.status.remove_class("error")

        if not hasattr(event.item, "path"):
            return

        if self.ctx.is_dirty:
            if self.confirm_action:
                action = self.confirm_action
                self.confirm_action = None
                self.ctx.is_dirty = False ## Mantive esse aqui também
                action()
                return

            self.confirm_action = lambda: self.load_file(str(event.item.path))
            self.status.update("Click again to discard changes")
            return
        self.load_file(str(event.item.path))
        
    def on_mount(self):
        if self.ctx.current_path and self.ctx.current_path.exists():
            self.load_file(str(self.ctx.current_path.absolute()))
        else:
            self.restore_session()
    
    def on_text_area_changed(self, event):
        if self._loading or self._status_locked:
            return
        editor = self.get_editor()
        self.ctx.is_dirty = (editor.text != self._original_text)
        dirty_flag = "*" if self.ctx.is_dirty else ""
        if self.ctx.current_path == None:
            self.status.update(f"SuperNanno | {editor.language} | UTF-8")
        else:    
            self.status.update(f"{self.ctx.current_path}{dirty_flag} | {editor.language} | UTF-8")

    def on_unmount(self) -> None:
        if self.ctx.current_path and not self.ctx.is_dirty:
            self.save_session_state(self.ctx.current_path)
            print()
            print()

    ###==================== ON EVENT ====================###

    async def __delayed_status__(self, delay, text):
        await asyncio.sleep(delay)
        self.status.update(text)

    async def __unlock_status_after__(self, delay, next_text):
        await asyncio.sleep(delay)
        self.status.remove_class("success")
        self.status.remove_class("info")
        self.status.remove_class("warning")
        self.status.remove_class("error")

        if next_text:
            self.status.update(next_text)
        else:
            self.status.update(self.get_default_status())
        self._status_locked = False

    def detect_language_from_content(self):
        editor = self.get_editor()
        try:
            lexer = guess_lexer(editor.text)
            if lexer.aliases:
                editor.language = lexer.aliases[0]
            else:
                editor.language = None
        except Exception:
            editor.language = None
        editor.refresh()

    def get_default_status(self):
        editor = self.get_editor()
        dirty_flag = "*" if self.ctx.is_dirty else ""

        if self.ctx.current_path:
            return f"{self.ctx.current_path}{dirty_flag} | {editor.language} | UTF-8"
        return f"SuperNanno | {editor.language} | UTF-8"

    def get_editor(self):
        return self.query_one("#editor", TextArea)

    def load_file(self, path_str, silent=False):
        try:
            path = Path(path_str)
            if path.is_dir():
                self.set_status(
                    text="(!): Cannot open a directory. Select a file instead",
                    delay=3,
                    next_text=f"SuperNanno | UTF-8",
                    status_type="warning"
                )
                return

            editor = self.get_editor()
            self._loading = True
            editor.text = path.read_text(encoding="utf-8")
            self._original_text = editor.text
            self.set_language(path)
            self.ctx.current_path = path
            self.ctx.is_dirty = False
            self._loading = False
            if not silent:
                self.status.update(f"{path} | {editor.language} | UTF-8")

        except Exception as e:
            self.set_status(
                text=f"(Error): Could not open file: {e}",
                delay=5,
                next_text=f"SuperNanno | Ready! | UTF-8",
                status_type="error"
            )

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

    def restore_session(self):
        config_path = Path("config.json")
        if not config_path.exists():
            return
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            last_file = config.get("settings", {}).get("session", {}).get("last_opened_file", {})
            if last_file:
                path = Path(last_file).expanduser()
                if path.exists() and path.is_file():
                    self._loading = True
                    self.load_file(str(path), silent=True)
                    self._loading = False
                    self.set_status(
                        f"(Session Restored): {path.name}",
                        delay=3,
                        next_text=self.get_default_status(),
                        status_type="info"
                    )
        except Exception as e:
            self.set_status(f"(Session Error): {e}", delay=3, status_type="error")

    def save_session_state(self, file_path):
        if not file_path:
            return
        config_path = Path("config.json")
        try:
            if config_path.exists():
                with open(config_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
            else:
                config = {}
            config.setdefault("settings", {})
            config["settings"].setdefault("session", {})
            config["settings"]["session"]["last_opened_file"] = str(file_path)

            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            # Security: Recreate config.json with default values
            self.set_status(f"(Save Session Error): {e}", delay=3, status_type="error")

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

        editor = self.get_editor()
        lang = language_map.get(ext)
        if lang:
            editor.language = lang
        else:
            try:
                lexer = guess_lexer(editor.text)
                editor.language = lexer.aliases[0] if lexer.aliases else None
            except Exception:
                editor.language = None
        editor.refresh()

    def set_status(self, text, delay=None, next_text=None, status_type="normal"):
        self._status_locked = True
        self.status.remove_class("success")
        self.status.remove_class("info")
        self.status.remove_class("warning")
        self.status.remove_class("error")

        if status_type == "success":
            self.status.add_class("success")
        elif status_type == "info":
            self.status.add_class("info")
        elif status_type == "warning":
            self.status.add_class("warning")
        elif status_type == "error":
            self.status.add_class("error")

        self.status.update(text)
        
        if hasattr(self, "_status_task") and self._status_task:
            self._status_task.cancel()

        if delay and next_text:
            self._status_task = self.run_worker(
                self.__unlock_status_after__(delay, next_text)
            )

if __name__ == "__main__":
    SuperNanno().run()