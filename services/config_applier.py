# services/config_applier.py

from pathlib import Path
from services.paths import get_backups_dir

class ConfigApplier:
    def __init__(self, ctx):
        self.ctx = ctx
        self.app = ctx.app

        self.handlers = {
            "backup": self.apply_backup,
            "backupdir": self.apply_backup_dir,
            "configwatcher": self.apply_config_watcher,
            "configwatcherinterval": self.apply_config_watcher_interval,
            "indenttype": self.apply_indent_type,
            "operatingdir": self.apply_operating_dir,
            "pathdisplay": self.apply_path_display,
            "restoresession": self.apply_restore_session,
            "sidebar": self.apply_sidebar,
            "sidebarwidth": self.apply_sidebar_width,
            "tabbehavior": self.apply_tab_behavior,
            "tabsize": self.apply_tab_size,
        }

    def apply(self, config):
        for key, handler in self.handlers.items():
            if key in config:
                handler(config[key])

    ###==================== HANDLERS ====================###

    def apply_backup(self, value):
        self.ctx.backup_enabled = value

    def apply_backup_dir(self, value):
        if not value or not str(value).strip():
            self.ctx.backup_dir = get_backups_dir()
            return

        self.ctx.backup_dir = Path(value).expanduser().resolve()

    def apply_config_watcher(self, value):
        self.ctx.config_watcher = value

    def apply_config_watcher_interval(self, value):
        try:
            self.ctx.config_watcher_interval = max(1, int(value))
        except (TypeError, ValueError):
            self.ctx.config_watcher_interval = 1

    def apply_indent_type(self, value):
        editor = self.ctx.editor
        editor.indent_type = value
        editor.refresh()
    
    def apply_operating_dir(self, value):
        if not value:
            return

        if self.app.explicit_file_open:
            return

        try:
            path = Path(value).expanduser().resolve()

            if not path.exists() or not path.is_dir():
                self.app.set_status(
                    f"(Config): invalid directory -> {path}",
                    delay=3,
                    status_type="warning"
                )
                return

            tree = self.app.directory_tree
            tree.path = str(path)
            tree.reload()

        except Exception as e:
            self.app.set_status(
                f"(Config): {e}",
                delay=3,
                status_type="warning"
            )
    
    def apply_path_display(self, value):
        allowed = {"full", "name"}
        if value not in allowed:
            return

        self.ctx.path_display = value

    def apply_restore_session(self, value):
        self.ctx.restore_session = bool(value)

    def apply_sidebar(self, value):
        sidebar = self.app.sidebar
        sidebar.display = value
        sidebar.refresh()

    def apply_sidebar_width(self, value):
        try:
            width = max(20, min(int(value), 80))
        except (TypeError, ValueError):
            return

        self.app.sidebar.styles.width = width
        self.app.sidebar.refresh()

    def apply_tab_behavior(self, value):
        editor = self.ctx.editor
        editor.tab_behavior = value
        editor.refresh()

    def apply_tab_size(self, value):
        editor = self.ctx.editor
        editor.indent_width = value
        editor.refresh()
