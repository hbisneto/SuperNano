# app.py

import argparse
import asyncio
import sys
from pathlib import Path

from pygments.lexers import guess_lexer
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DirectoryTree,
    TextArea,
    ListView,
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
    button_pressed,
    directory_tree_selected,
    input_changed,
    input_submitted,
    key,
    list_view_selected,
    mount,
    text_area_changed,
    unmount
)

from services.app_context import AppContext
from services.config_applier import ConfigApplier
from ui.bindings import BINDINGS, CSS_FILE, WELCOME
from ui.settings.screen import SettingsScreen
from ui.layout import create_layout

def parse_args():
    parser = argparse.ArgumentParser(
        prog="supernanno",
        description="Modern Nano-like terminal text editor"
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="File to open"
    )

    return parser.parse_args()

class SuperNanno(App):
    CSS_PATH = CSS_FILE
    BINDINGS = BINDINGS

    def __init__(self, file_path: str | None = None):
        super().__init__()
        self.input_mode = None
        self.temp_file = None
        self._loading = False
        self.confirm_action = None
        self._confirm_quit = False
        self._status_locked = False
        self.explicit_file_open = bool(file_path)
        self.ctx = AppContext(self)
        self.config_applier = ConfigApplier(self)

        if file_path:
            self.ctx.current_path = Path(file_path)

    def compose(self) -> ComposeResult:
        (header, 
            self.sidebar, 
            main_content, 
            footer, 
            self.directory_tree, 
            self.search_bar, 
            self.path_input, 
            self.editor, 
            self.status,
            self.search_container,
            self.path_container
        ) = create_layout()

        self.editor.load_text(WELCOME)

        yield header
        yield Horizontal(
            self.sidebar,
            main_content
        )
        yield footer

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

    def action_show_settings(self):
        self.push_screen(SettingsScreen())

    ###==================== ACTIONS ====================###

    ###==================== ON EVENT ====================###
    
    def on_button_pressed(self, event):
        button_pressed.handle(self.ctx, event)

    def on_config_reload(self):
        self.config_applier.apply(self.ctx.config.data)

        self.set_status(
            "(Config Reloaded)",
            delay=2,
            status_type="info"
        )

    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected):
        directory_tree_selected.handle(self.ctx, event)

    def on_input_changed(self, event):
        input_changed.handle(self.ctx, event)

    def on_input_submitted(self, event: Input.Submitted):
        input_submitted.handle(self.ctx, event)

    def on_key(self, event):
        key.handle(self.ctx, event)

    def on_list_view_selected(self, event: ListView.Selected):
        list_view_selected.handle(self.ctx, event)
        
    def on_mount(self):
        mount.handle(self.ctx)

        if self.ctx.config.get("config_watcher", True):
            self.run_worker(
                self.__watch_config__(),
                name="config_watcher"
            )
    
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

    async def __watch_config__(self):
        while True:
            interval = self.ctx.config.get("config_watcher_interval", 1)
            changed = self.ctx.config.reload_rc_if_changed()

            if changed:
                self.on_config_reload()
            await asyncio.sleep(interval)

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
        lang = "text" if (lang := getattr(editor, "language", None)) is None else lang
        
        if self.ctx.current_path:
            return f"{self.ctx.current_path}{dirty_flag} | {lang} | UTF-8"
        return f"SuperNanno | {lang} | UTF-8"

    def get_editor(self):
        return self.query_one("#editor", TextArea)

    def load_file(self, path_str, silent=False):
        """Load a file and update the editor content, language, and status."""
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

            self.set_language(path)

            self._loading = True
            editor.load_text(content)
            self._loading = False

            self.ctx.editor_state.mark_saved(content)
            self.ctx.current_path = path
            self.ctx.is_dirty = False

            self.save_session_state(path)

            editor.focus()

            if not silent:
                self.ctx.status.set(
                    f"Opened: {path.name}",
                    delay=2,
                    next_text=self.get_default_status(),
                    status_type="info"
                )

        except Exception as e:
            self.ctx.status.error(
                f"(Error loading file): {e}",
                delay=5,
                status_type="error"
            )

    def prompt_save_as(self):
        path_container = self.query_one("#path_container")
        path_container.display = True
        input_widget = self.query_one("#path_input", Input)
        input_widget.display = True
        input_widget.placeholder = "Save as: ./file.txt"
        input_widget.value = "./"
        input_widget.focus()
        self.input_mode = "save"
        self.status.update("Enter path to save file")

    def restore_session(self):
        if self.explicit_file_open:
            return

        if not self.ctx.config:
            return

        if not self.ctx.config.get("restore_last_session", True):
            return

        last_file = self.ctx.session.get_last_file()
        if not last_file:
            return

        path = Path(last_file)
        if path.exists():
            self.load_file(str(path), silent=True)
            self.ctx.status.set(
                f"(Session Restored): {path.name}",
                delay=3,
                next_text=self.get_default_status(),
                status_type="info"
            )

    def save_session_state(self, file_path):
        if self.explicit_file_open:
            return

        if not self.ctx.session:
            return

        if not file_path:
            return

        self.ctx.session.set_last_file(str(file_path))
        self.ctx.session.save()
            # Security: Recreate config.json with default values
            # self.set_status(f"(Save Session Error): {e}", delay=3, status_type="error")

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
        editor.language = language_map.get(ext)

        if not editor.language:
            try:
                lexer = guess_lexer(editor.text)
                editor.language = lexer.aliases[0] if lexer.aliases else None
            except Exception:
                editor.language = None

        editor.refresh()

    def set_state(self, state):
        if self.ctx.state:
            self.ctx.state.on_exit(self.ctx)

        self.ctx.state = state

        if state:
            state.on_enter(self.ctx)

    def set_status(self, text, delay=None, next_text=None, status_type="normal"):
        """Update the status bar in a safe manner."""
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

        if delay is not None:
            next_text = next_text or self.get_default_status()
            self._status_task = self.run_worker(
                self.__unlock_status_after__(delay, next_text),
                name="status_unlock"
            )
def main():
    args = parse_args()
    SuperNanno(file_path=args.file).run()

if __name__ == "__main__":
    main()