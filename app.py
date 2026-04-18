# app.py

import asyncio
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

from cli.parser import parse_cli_args

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

from search.controller import SearchController
from services.app_context import AppContext
from ui.bindings import BINDINGS, CSS_FILE, WELCOME
from ui.settings.screen import SettingsScreen
from ui.layout import create_layout
class SuperNanno(App):
    CSS_PATH = CSS_FILE
    BINDINGS = BINDINGS

    def __init__(self, cli_args=None):
        super().__init__()
        self.cli_args = cli_args
        self.input_mode = None
        self.temp_file = None
        self._loading = False
        self.confirm_action = None
        self._confirm_quit = False
        self.explicit_file_open = bool(cli_args and cli_args.file)
        self.ctx = AppContext(self)
        if cli_args:
            if cli_args.backup:
                self.ctx.backup_enabled = True

            if cli_args.backup_dir:
                self.ctx.backup_dir = Path(cli_args.backup_dir).expanduser().resolve()

        if cli_args and cli_args.view_mode:
            self.ctx.read_only = True
        
        if cli_args and cli_args.file:
            self.ctx.current_path = Path(cli_args.file)

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
        self.ctx.config_applier.apply(self.ctx.config.data)
        self.ctx.status.info("(Config Reloaded)")

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
        self.ctx.config_applier.apply(self.ctx.config.data)
        mount.handle(self.ctx)

        if self.ctx.config_watcher:
            self.run_worker(
                self.__watch_config__(),
                name="config_watcher"
            )
    
    def on_text_area_changed(self, event):
        text_area_changed.handle(self.ctx)

    def on_unmount(self) -> None:
        unmount.handle(self.ctx)

    ###==================== ON EVENT ====================###

    async def __watch_config__(self):
        while True:
            interval = self.ctx.config_watcher_interval
            changed = self.ctx.config.reload_rc_if_changed()

            if changed:
                self.on_config_reload()
            await asyncio.sleep(interval)

    def detect_language_from_content(self):
        editor = self.ctx.editor
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
        path = self.ctx.current_path
        if path:
            if self.ctx.path_display == "name":
                path_str = path.name
            else:
                path_str = str(path)
        else:
            path_str = "SuperNanno"

        editor = self.ctx.editor
        dirty_flag = "*" if self.ctx.is_dirty else ""
        lang = "text" if (lang := getattr(editor, "language", None)) is None else lang
        
        if self.ctx.read_only:
            return f"(READ ONLY): {path_str} | {lang} | UTF-8"
            
        if path:
            return f"{path_str}{dirty_flag} | {lang} | UTF-8"

        return f"{path_str} | {lang} | UTF-8"

    def load_file(self, path_str, silent=False):
        """Load a file and update the editor content, language, and status."""
        try:
            path = Path(path_str)

            if path.is_dir():
                self.ctx.status.warning("(File Operation): Cannot open a directory\n >> Choose a file to open it")
                return

            content = self.ctx.file_manager.read(path)
            editor = self.ctx.editor

            self.ctx.current_path = path
            self._loading = True
            editor.load_text(content)
            self.set_language(path)
            self.editor.read_only = self.ctx.read_only
            self._loading = False

            self.ctx.editor_state.mark_saved(content)
            self.ctx.is_dirty = False

            self.save_session_state(path)

            editor.focus()

            if not silent:
                self.ctx.status.info(f"(Opened): {path.name}")

            if self.cli_args:
                if self.cli_args.line:
                    row = max(0, self.cli_args.line - 1)
                    col = self.cli_args.column
                    editor.cursor_location = (row, col)

                elif self.cli_args.search:
                    SearchController().search(self.ctx, self.cli_args.search)

        except Exception as e:
            self.ctx.status.error(f"(Error loading file): {e}")

    def prompt_save_as(self):
        path_container = self.query_one("#path_container")
        path_container.display = True
        input_widget = self.query_one("#path_input", Input)
        input_widget.display = True
        input_widget.placeholder = "Save as: ./file.txt"
        input_widget.value = "./"
        input_widget.focus()
        self.input_mode = "save"
        self.ctx.status.persist("Enter path to save file")

    def restore_session(self):
        if self.explicit_file_open:
            return

        if not self.ctx.config:
            return

        if not self.ctx.restore_session:
            return

        last_file = self.ctx.session.get_last_file()
        if not last_file:
            return

        path = Path(last_file)
        if path.exists():
            self.load_file(str(path), silent=True)
            self.ctx.status.info(f"(Session Restored): {path.name}")

    def save_session_state(self, file_path):
        if self.explicit_file_open:
            return

        if not self.ctx.session:
            return

        if not file_path:
            return

        self.ctx.session.set_last_file(str(file_path))
        self.ctx.session.save()

    def set_language(self, path: Path):
        ext = path.suffix.lower()
        language_map = {
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".css": "css",
            ".html": "html",
            ".js": "javascript",
            ".json": "json",
            ".md": "markdown",
            ".py": "python",
            ".sh": "bash",
            ".ts": "typescript",
        }

        editor = self.ctx.editor
        lang = language_map.get(ext)

        try:
            editor.language = lang
        except Exception:
            editor.language = None

        if not editor.language:
            try:
                lexer = guess_lexer(editor.text[:1000])
                alias = lexer.aliases[0] if lexer.aliases else None
                try:
                    editor.language = alias
                except Exception:
                    editor.language = None
            except Exception:
                editor.language = None

        editor.refresh()

    def set_state(self, state):
        if self.ctx.state:
            self.ctx.state.on_exit(self.ctx)

        self.ctx.state = state

        if state:
            state.on_enter(self.ctx)

def main():
    cli_args = parse_cli_args()
    if cli_args.help:
        from cli.constants import HELP_TEXT
        print(HELP_TEXT)
        return

    if cli_args.version:
        from cli.constants import VERSION
        print(VERSION)
        return
    SuperNanno(cli_args=cli_args).run()

if __name__ == "__main__":
    main()