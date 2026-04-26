# app.py

import asyncio
import sys
from cli.constants import HELP_TEXT
from cli.constants import VERSION
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
    unmount,
)
from handlers import (
    new,
    open_file,
    read,
    save,
    toggle_sidebar,
    quit,
)
from pathlib import Path
from services.app_context import AppContext
from states.search import SearchState
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import (
    Input,
    DirectoryTree,
    ListView
)
from ui.bindings import (
    BINDINGS, 
    CSS_FILE,
    WELCOME
)
from ui.layout import create_layout
from ui.settings.screen import SettingsScreen

class SuperNanno(App):
    BINDINGS = BINDINGS
    CSS_PATH = CSS_FILE

    def __init__(self, cli_args=None):
        super().__init__()
        self.cli_args = cli_args
        self.input_mode = None
        self._loading = False
        self._confirm_quit = False
        self.welcome_text = WELCOME
        self.explicit_file_open = bool(cli_args and cli_args.file)
        self.ctx = AppContext(self)

        if cli_args:
            if cli_args.backup:
                self.ctx.backup_enabled = True
            if cli_args.backup_dir:
                self.ctx.backup_dir = Path(cli_args.backup_dir).expanduser().resolve()
            if cli_args.view_mode:
                self.ctx.read_only = True
            if cli_args.file:
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
            self.path_container,
            self.startup_view
        ) = create_layout()
        self.in_startup = True

        yield header
        yield Horizontal(self.sidebar, main_content)
        yield footer

    # ==================== ACTIONS ====================

    def action_new_file(self):
        new(self.ctx)

    def action_open_path(self):
        open_file(self.ctx)

    def action_save(self):
        save(self.ctx)

    def action_read_file(self):
        read(self.ctx)

    def action_quit(self):
        quit(self.ctx)

    def action_search(self):
        self.ctx.set_state(SearchState())

    def action_show_hide_sidebar(self):
        toggle_sidebar(self.ctx)

    def action_show_settings(self):
        self.push_screen(SettingsScreen())

    # ==================== EVENTS ====================

    def on_button_pressed(self, event):
        button_pressed.handle(self.ctx, event)

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
        self.apply_startup_policy()
        self.ctx.status.default()

        if self.ctx.config_watcher:
            self.run_worker(self.__watch_config__(), name="config_watcher")

    def on_text_area_changed(self, event):
        text_area_changed.handle(self.ctx)

    def on_unmount(self):
        unmount.handle(self.ctx)

    def on_config_reload(self):
        self.ctx.config_applier.apply(self.ctx.config.data)
        self.ctx.status.info("(Config): Reloaded")

    # ==================== AUX METHODS ====================

    async def __watch_config__(self):
        while True:
            changed = self.ctx.config.reload_rc_if_changed()
            if changed:
                self.on_config_reload()
            await asyncio.sleep(self.ctx.config_watcher_interval)

    def apply_startup_policy(self):
        if self.ctx.restore_session and self.ctx.editor.text.strip():
            self.in_startup = False
            self.startup_view.display = False
            self.editor.display = True

    def prompt_save_as(self):
        if self.path_container:
            self.path_container.display = True
        input_widget = self.query_one("#path_input", Input)
        input_widget.display = True
        input_widget.placeholder = "Enter path to save (e.g. ./file.txt)"
        input_widget.value = "./"
        input_widget.focus()
        self.input_mode = "save"
        self.ctx.status.persist("(Path): Enter path to save file")

def main():
    cli_args = parse_cli_args()
    if cli_args.help:
        print(HELP_TEXT)
        return
    if cli_args.version:
        print(VERSION)
        return
    if cli_args.invalid_arg:
        print(f'supernanno: unrecognized option `{cli_args.invalid_arg}`')
        print(HELP_TEXT)
        sys.exit(1)

    SuperNanno(cli_args=cli_args).run()

if __name__ == "__main__":
    main()