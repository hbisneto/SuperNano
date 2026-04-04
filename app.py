# app.py

from __future__ import annotations
import asyncio
import sys
from pathlib import Path

from pygments.lexers import guess_lexer
from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import (
    DirectoryTree,
    Static,
    TextArea,
    ListView,
    ListItem,
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
from ui.bindings import BINDINGS, WELCOME
from ui.settings.screen import SettingsScreen
from ui.layout import create_layout

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
        # Centraliza a criação do layout
        (header, 
            self.sidebar, 
            main_content, 
            footer, 
            self.directory_tree, 
            self.search_bar, 
            self.path_input, 
            self.editor, 
            self.status,
            self.search_container,   # novo
            self.path_container) = create_layout()

        # Define o texto inicial do editor
        self.editor.load_text(WELCOME)

        # Monta a tela principal
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
        lang = getattr(editor, 'language', None) or "text"

        if self.ctx.current_path:
            return f"{self.ctx.current_path}{dirty_flag} | {lang} | UTF-8"
        return f"SuperNanno | {lang} | UTF-8"

    def get_editor(self):
        return self.query_one("#editor", TextArea)

    def load_file(self, path_str, silent=False):
        """Carrega um arquivo e atualiza o editor + session + config"""
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
            # editor.refresh()

            # if not silent:
            #     self.ctx.status.set(
            #         f"Opened: {path.name}",
            #         delay=2,
            #         next_text=self.get_default_status(),
            #         status_type="info"
            #     )

        except Exception as e:
            self.ctx.status.set(
                f"(Error loading file): {e}",
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
        """Restaura o último arquivo aberto usando o ConfigManager"""
        if not self.ctx.config.get("settings.startup.restore_last_session", True):
            return

        last_file = self.ctx.config.get("settings.session.last_opened_file", "")
        if not last_file:
            return

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

    def save_session_state(self, file_path: Path | None):
        """Salva o último arquivo aberto"""
        if not file_path:
            return
        self.ctx.config.set("settings.session.last_opened_file", str(file_path))
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
                editor.language = lexer.aliases[0] if lexer.aliases else "text"
            except Exception:
                editor.language = "text"

        editor.refresh()

    def set_state(self, state):
        if self.ctx.state:
            self.ctx.state.on_exit(self.ctx)

        self.ctx.state = state

        if state:
            state.on_enter(self.ctx)

    def set_status(self, text, delay=None, next_text=None, status_type="normal"):
        """Atualiza o status bar de forma segura."""
        self._status_locked = True

        # Remove todas as classes de cor
        self.status.remove_class("success")
        self.status.remove_class("info")
        self.status.remove_class("warning")
        self.status.remove_class("error")

        # Aplica a cor correta
        if status_type == "success":
            self.status.add_class("success")
        elif status_type == "info":
            self.status.add_class("info")
        elif status_type == "warning":
            self.status.add_class("warning")
        elif status_type == "error":
            self.status.add_class("error")

        self.status.update(text)

        # Cancela tarefa anterior se existir
        if hasattr(self, "_status_task") and self._status_task:
            self._status_task.cancel()

        # Se tiver delay, agenda a restauração do status
        if delay is not None:
            next_text = next_text or self.get_default_status()
            self._status_task = self.run_worker(
                self.__unlock_status_after__(delay, next_text),
                name="status_unlock"
            )

if __name__ == "__main__":
    SuperNanno().run()