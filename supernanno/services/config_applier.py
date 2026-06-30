# services/config_applier.py

from pathlib import Path
from ..services.paths import get_backups_dir


class ConfigApplier:
    def __init__(self, ctx):
        self.ctx = ctx
        self.app = ctx.app

        self.handlers = {
            "backup":                self.apply_backup,
            "backupdir":             self.apply_backup_dir,
            "configwatcher":         self.apply_config_watcher,
            "configwatcherinterval": self.apply_config_watcher_interval,
            "debug":                 self.apply_debug,
            "indenttype":            self.apply_indent_type,
            "linenumbers":          self.apply_line_numbers,
            "operatingdir":          self.apply_operating_dir,
            "pathdisplay":           self.apply_path_display,
            "restoresession":        self.apply_restore_session,
            "sidebar":               self.apply_sidebar,
            "sidebarwidth":          self.apply_sidebar_width,
            "tabbehavior":           self.apply_tab_behavior,
            "tabsize":               self.apply_tab_size,
        }

    def apply(self, config: dict) -> None:
        for key, handler in self.handlers.items():
            if key in config:
                try:
                    handler(config[key])
                except Exception as e:
                    self.ctx.errors.handle(
                        e,
                        action="CONFIG_APPLY",
                        event_origin=f"config_applier.{key}",
                        extra={"config_key": key, "config_value": str(config[key])},
                    )

    # ─── Handlers ────────────────────────────────────────────────────

    def apply_backup(self, value):
        self.ctx.backup_enabled = bool(value)

    def apply_backup_dir(self, value):
        if not value or not str(value).strip():
            self.ctx.backup_dir = get_backups_dir()
            return
        self.ctx.backup_dir = Path(value).expanduser().resolve()

    def apply_config_watcher(self, value):
        self.ctx.config_watcher = bool(value)

    def apply_config_watcher_interval(self, value):
        try:
            self.ctx.config_watcher_interval = max(1, int(value))
        except (TypeError, ValueError) as e:
            self.ctx.logs.warning(
                f"(ConfigApplier): Invalid configwatcherinterval '{value}', using 1 — {e}",
                action="CONFIG_APPLY_WATCHER_INTERVAL",
            )
            self.ctx.config_watcher_interval = 1

    def apply_debug(self, value):
        self.ctx.debug_mode = bool(value)
        if self.ctx.debug_mode:
            self.ctx.logs.info(
                "(Config): Debug mode enabled",
                action="CONFIG_APPLY_DEBUG",
            )

    def apply_indent_type(self, value):
        editor = self.ctx.editor
        try:
            editor.indent_type = value
            editor.refresh()
        except Exception as e:
            self.ctx.logs.warning(
                f"(ConfigApplier): Could not apply indent_type '{value}' — {e}",
                action="CONFIG_APPLY_INDENT_TYPE",
            )

    def apply_line_numbers(self, value):
        """Aplica visibilidade dos números de linha sem quebrar highlighting."""
        try:
            show = bool(value)
            self.ctx.line_numbers = show
            
            editor = getattr(self.ctx, 'editor', None)
            if not editor:
                return

            # Tenta vários caminhos comuns no Textual
            changed = False
            
            if hasattr(editor, "show_line_numbers"):
                if editor.show_line_numbers != show:
                    editor.show_line_numbers = show
                    changed = True
                    
            elif hasattr(editor, "gutter"):
                if hasattr(editor.gutter, "show_line_numbers"):
                    if getattr(editor.gutter, "show_line_numbers", None) != show:
                        editor.gutter.show_line_numbers = show
                        changed = True
                # Alguns widgets têm _line_numbers ou similar
                elif hasattr(editor.gutter, "_show_line_numbers"):
                    editor.gutter._show_line_numbers = show
                    changed = True

            # Força refresh sem perder highlighting
            if changed:
                try:
                    editor.refresh()
                    # Reaplica linguagem se necessário
                    if hasattr(editor, "language") and editor.language:
                        # Isso força o highlighter a ser reavaliado
                        editor._highlight_timer = None  # força re-highlight em alguns casos
                except Exception:
                    pass

            self.ctx.logs.debug(f"Line numbers set to: {show}")
            
        except Exception as e:
            self.ctx.logs.warning(
                f"(ConfigApplier): Could not apply linenumbers — {e}",
                action="CONFIG_APPLY_LINE_NUMBERS",
            )

    def apply_operating_dir(self, value):
        if not value:
            return

        if self.app.explicit_file_open:
            return

        try:
            path = Path(value).expanduser().resolve()

            if not path.exists() or not path.is_dir():
                self.ctx.status.warning(f"(Config): Invalid directory \"{path}\"")
                self.ctx.logs.warning(
                    f"(ConfigApplier): operatingdir is not a valid directory — {path}",
                    action="CONFIG_APPLY_OPERATING_DIR",
                    path=path,
                )
                return

            tree = self.app.directory_tree
            tree.path = str(path)
            tree.reload()

            self.ctx.logs.info(
                f"(ConfigApplier): operatingdir applied — {path}",
                action="CONFIG_APPLY_OPERATING_DIR",
                path=path,
            )

        except Exception as e:
            self.ctx.status.warning(f"(Config): Failed to apply directory — {e}")
            self.ctx.logs.warning(
                f"(ConfigApplier): Failed to apply operatingdir '{value}' — {e}",
                action="CONFIG_APPLY_OPERATING_DIR",
                path=value,
            )

    def apply_path_display(self, value):
        allowed = {"full", "name"}
        if value not in allowed:
            self.ctx.logs.warning(
                f"(ConfigApplier): Unknown pathdisplay value '{value}', "
                f"expected one of {allowed}",
                action="CONFIG_APPLY_PATH_DISPLAY",
            )
            return
        self.ctx.path_display = value

    def apply_restore_session(self, value):
        self.ctx.restore_session = bool(value)

    def apply_sidebar(self, value):
        try:
            sidebar = self.app.sidebar
            sidebar.display = bool(value)
            sidebar.refresh()
        except Exception as e:
            self.ctx.logs.warning(
                f"(ConfigApplier): Could not apply sidebar visibility — {e}",
                action="CONFIG_APPLY_SIDEBAR",
            )

    def apply_sidebar_width(self, value):
        try:
            width = max(20, min(int(value), 80))
            self.app.sidebar.styles.width = width
            self.app.sidebar.refresh()
        except (TypeError, ValueError) as e:
            self.ctx.logs.warning(
                f"(ConfigApplier): Invalid sidebarwidth '{value}' — {e}",
                action="CONFIG_APPLY_SIDEBAR_WIDTH",
            )
        except Exception as e:
            self.ctx.logs.warning(
                f"(ConfigApplier): Could not apply sidebarwidth — {e}",
                action="CONFIG_APPLY_SIDEBAR_WIDTH",
            )

    def apply_tab_behavior(self, value):
        editor = self.ctx.editor
        try:
            editor.tab_behavior = value
            editor.refresh()
        except Exception as e:
            self.ctx.logs.warning(
                f"(ConfigApplier): Could not apply tab_behavior '{value}' — {e}",
                action="CONFIG_APPLY_TAB_BEHAVIOR",
            )

    def apply_tab_size(self, value):
        editor = self.ctx.editor
        try:
            editor.indent_width = value
            editor.refresh()
        except Exception as e:
            self.ctx.logs.warning(
                f"(ConfigApplier): Could not apply tab_size '{value}' — {e}",
                action="CONFIG_APPLY_TAB_SIZE",
            )
