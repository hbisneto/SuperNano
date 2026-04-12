# services/config_applier.py
from pathlib import Path

class ConfigApplier:
    def __init__(self, ctx):
        self.ctx = ctx
        self.app = ctx.app

        self.handlers = {
            "auto_backup": self.apply_auto_backup,
            "config_watcher": self.apply_watcher,
            "config_watcher_interval": self.apply_watcher_interval,
            "current_directory": self.apply_current_directory,
            "indent_type": self.apply_indent_type,
            "restore_last_session": self.apply_restore_last_session,
            "sidebar_visibility": self.apply_sidebar_visibility,
            "sidebar_width": self.apply_sidebar_width,
            "tab_behavior": self.apply_tab_behavior,
            "tab_size": self.apply_tab_size,
        }

    def apply(self, config):
        for key, handler in self.handlers.items():
            if key in config:
                handler(config[key])

    ###==================== HANDLERS ====================###

    def apply_auto_backup(self, value):
        self.ctx.auto_backup_enabled = value

    def apply_current_directory(self, value):
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
    
    def apply_indent_type(self, value):
        editor = self.app.get_editor()
        editor.indent_type = value
        editor.refresh()

    def apply_restore_last_session(self, value):
        self.ctx.restore_last_session = bool(value)

    def apply_sidebar_visibility(self, value):
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
        editor = self.app.get_editor()
        editor.tab_behavior = value
        editor.refresh()

    def apply_tab_size(self, value):
        editor = self.app.get_editor()
        editor.indent_width = value
        editor.refresh()

    def apply_watcher(self, value):
        self.ctx.config_watcher = value

    def apply_watcher_interval(self, value):
        try:
            self.ctx.config_watcher_interval = max(1, int(value))
        except (TypeError, ValueError):
            self.ctx.config_watcher_interval = 1