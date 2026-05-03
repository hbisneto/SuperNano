# services/app_context.py

from pathlib import Path
from pygments.lexers import guess_lexer

from core.editor import EditorState
from core.file_manager import FileManager
from core.status import StatusService
from services.config_manager import ConfigManager
from services.session_manager import SessionManager
from services.config_applier import ConfigApplier
from plugins.registry import PluginRegistry
from states.search import SearchState


class AppContext:
    def __init__(self, app):
        self.app = app

        self.current_path: Path | None = None
        self.state = None
        self.pending_action = None

        # Settings
        self.config_watcher = True
        self.config_watcher_interval = 1
        self.restore_session = True
        self.backup_enabled = False
        self.backup_dir: Path | None = None
        self.read_only = False
        self.path_display = "full"

        # Services
        self.editor_state = EditorState()
        self.file_manager = FileManager()
        self.status = StatusService(self, debug=True)
        self.config = ConfigManager()
        self.session = SessionManager(
            create_if_missing=not getattr(app, "explicit_file_open", False)
        )
        self.config_applier = ConfigApplier(self)
        self.plugins = PluginRegistry()
        self.word_count = 0
        self.char_count = 0
        self.file_size = 0
        self.encoding = "UTF-8"
        self.eol = "LF"
        self.read_time = 0

    @property
    def editor(self):
        return self.app.editor

    @property
    def is_dirty(self) -> bool:
        if not self.editor:
            return False
        return self.editor_state.is_dirty(self.editor.text)

    def set_state(self, new_state):
        if self.state and hasattr(self.state, "on_exit"):
            self.state.on_exit(self)

        self.state = new_state

        if self.state and hasattr(self.state, "on_enter"):
            self.state.on_enter(self)

    @staticmethod
    def format_size(size):
        if size < 1024:
            return f"{size} bytes"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        else:
            return f"{size / (1024 * 1024):.1f} MB"

    def get_default_status(self) -> str:
        if not self.editor:
            return "SuperNanno | Ready"

        path = self.current_path
        path_str = path.name if path and self.path_display == "name" else str(path or "SuperNanno")
        dirty = "*" if self.is_dirty else ""

        lang = getattr(self.editor, "language", None) or "text"

        try:
            row, col = self.editor.cursor_location
            row += 1
            col += 1
        except Exception:
            row, col = 1, 1

        # ==================== STATS ==================== #

        stats_parts = []

        if self.word_count > 0:
            stats_parts.append(f"Words {self.word_count},")

        if self.char_count > 0:
            stats_parts.append(f"Chars {self.char_count}")

        stats = f" | {' '.join(stats_parts)}" if stats_parts else ""

        # ==================== EXTRA ==================== #

        size = f" | {self.format_size(self.file_size)}" if self.file_size else ""
        eol = f" | {self.eol}" if self.eol else ""
        encoding = f" | {self.encoding}" if self.encoding else ""
        read_time = f" | ~{self.read_time}m read" if self.read_time else ""

        base = (
            f"{path_str}{dirty} | {lang} | Ln {row}, Col {col}"
            f"{stats}{size}{read_time}{eol}{encoding}"
        )

        if self.read_only:
            return f"(READ-ONLY): {base}"

        return base

    def mark_clean(self):
        if self.editor:
            self.editor_state.mark_saved(self.editor.text)

    def check_dirty_before(self, action, message: str = "(Editor): Unsaved changes") -> bool:
        if not self.is_dirty:
            action()
            self.clear_pending_action()
            return True

        if self.pending_action is not None:
            self.pending_action()
            self.pending_action = None
            action()
            return True

        self.pending_action = action
        self.status.warning(f"{message} — press again to confirm")
        return False

    def clear_pending_action(self):
        self.pending_action = None

    def set_language(self, path: Path):
        ext = path.suffix.lower()

        language_map = {
            ".c": "c", ".cpp": "cpp", ".cs": "csharp",
            ".css": "css", ".html": "html", ".js": "javascript",
            ".json": "json", ".md": "markdown", ".py": "python",
            ".sh": "bash", ".ts": "typescript",
        }

        editor = self.editor
        lang = language_map.get(ext)

        try:
            editor.language = lang
        except Exception:
            editor.language = None

        if not editor.language:
            try:
                lexer = guess_lexer(editor.text[:1000])
                alias = lexer.aliases[0] if lexer.aliases else None
                editor.language = alias
            except Exception:
                editor.language = None

        editor.refresh()

    def save_session_state(self, file_path: Path | str):
        if getattr(self.app, "explicit_file_open", False) or not file_path:
            return

        self.session.set_last_file(str(file_path))
        self.session.save()

    @property
    def path_container(self):
        return getattr(self.app, "path_container", None)

    @property
    def search_container(self):
        return getattr(self.app, "search_container", None)

    @property
    def directory_tree(self):
        return getattr(self.app, "directory_tree", None)

    @property
    def sidebar(self):
        return getattr(self.app, "sidebar", None)

    def goto_line_column(self, line: int | None, column: int = 0):
        if line is None:
            return

        row = max(0, line - 1)
        col = max(0, column)

        editor = self.editor

        try:
            editor.cursor_location = (row, col)
            editor.scroll_to(y=row, animate=False)

            def reset_horizontal_scroll():
                try:
                    editor.scroll_to(x=0, animate=False)
                    if hasattr(editor, 'scroll_x'):
                        editor.scroll_x = 0
                except Exception:
                    pass

            self.app.call_after_refresh(reset_horizontal_scroll)

        except Exception:
            try:
                editor.cursor_location = (row, 0)
                editor.scroll_to(y=row, x=0, animate=False)
            except Exception:
                pass

    # ==================== PLUGIN SUPPORT ====================

    def register_plugin_command(self, name: str, func: callable):
        self.plugins.register_command(name, func)

    def register_plugin_hook(self, hook_name: str, func: callable):
        self.plugins.register_hook(hook_name, func)

    def execute_plugin_command(self, name: str, *args, **kwargs) -> bool:
        return self.plugins.execute_command(name, self, *args, **kwargs)

    def execute_hook(self, hook_name: str, *args, **kwargs):
        self.plugins.execute_hook(hook_name, self, *args, **kwargs)