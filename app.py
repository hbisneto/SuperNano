import asyncio
import json
import sys
from pathlib import Path

from pygments.lexers import guess_lexer
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    Static, 
    TextArea, 
    ListView, 
    ListItem, 
    Header, 
    Footer, 
    Input
)

from commands import (
    new_file,
    open_file,
    quit,
    read_file,
    save_file,
    search,
    toggle_sidebar
)

from events import (
    input_submitted,
    key,
    list_view_selected,
    mount,
    text_area_changed,
    unmount
)

from services.app_context import AppContext
from ui.bindings import BINDINGS, TEXT

class SuperNanno(App):
    CSS_PATH = "style.tcss"
    BINDINGS = BINDINGS

    def __init__(self):
        super().__init__()
        self.input_mode = None
        self.temp_file = None
        self._loading = False
        self.confirm_action = None
        self._confirm_quit = False
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

        self.sidebar = Vertical(
            Static("FILES", classes="title"),
            self.file_list,
            id="sidebar"
        )
        yield Horizontal(
            self.sidebar,
            Vertical(
                self.editor,
                self.path_input,
                self.status,
                id="main"
            )
        )
        
        yield Footer()

    ###==================== ACTIONS ====================###

    def action_new_file(self):
        new_file.execute(self.ctx)
        
    def action_open_path(self):
        open_file.execute(self.ctx)

    def action_quit(self):
        quit.execute(self.ctx)

    def action_read_file(self):
        read_file.execute(self.ctx)

    def action_save(self):
        save_file.execute(self.ctx)

    def action_search(self):
        search.execute(self.ctx)

    def action_show_hide_sidebar(self):
        toggle_sidebar.execute(self.ctx)

    ###==================== ACTIONS ====================###

    ###==================== ON EVENT ====================###
    
    def on_input_submitted(self, event: Input.Submitted):
        input_submitted.handle(self.ctx, event)

    def on_key(self, event):
        key.handle(self.ctx, event)

    def on_list_view_selected(self, event: ListView.Selected):
        list_view_selected.handle(self.ctx, event)
        
    def on_mount(self):
        mount.handle(self.ctx)
    
    def on_text_area_changed(self, event):
        text_area_changed.handle(self.ctx)

    def on_unmount(self) -> None:
        unmount.handle(self.ctx)

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
                self.ctx.status.set(
                    "(File Operation): Cannot open a directory\n >> Choose a file to open it",
                    delay=3,
                    next_text=self.get_default_status(),
                    status_type="warning"
                )
                return

            content = self.ctx.file_manager.read(path)
            editor = self.get_editor()
            self._loading = True
            editor.text = content
            self._loading = False
            self.ctx.editor_state.mark_saved(content)
            self.ctx.current_path = path
            self.ctx.is_dirty = False
            self.set_language(path)

            if not silent:
                self.ctx.status.set(f"{path} loaded", delay=1, next_text=self.get_default_status())

        except Exception as e:
            self.ctx.status.set(
                f"(Error): {e}",
                delay=5,
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
                    self.ctx.status.set(
                        f"(Session Restored): {path.name}",
                        delay=3,
                        next_text=self.get_default_status(),
                        status_type="info"
                    )
        except Exception as e:
            self.ctx.status.set(
                f"(Session Error): {e}",
                delay=3,
                next_text=self.get_default_status(),
                status_type="error"
            )

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
            # self.set_status(f"(Save Session Error): {e}", delay=3, status_type="error")
            self.ctx.status.set(f'(Save Session Error): {e}', delay=3, status_type="error")

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