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

        # respeita arquivo passado por CLI
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

            # troca a raiz do explorer
            tree.path = str(path)

            # força redraw
            tree.reload()

        except Exception as e:
            self.app.set_status(
                f"(Config): {e}",
                delay=3,
                status_type="warning"
            )

    def apply_tab_size(self, value):
        editor = self.app.get_editor()
        editor.tab_behavior = "indent"
        editor.indent_type = "spaces"
        editor.indent_width = value
        editor.refresh()

    def apply_watcher(self, value):
        # self.app.config_watcher = value
        self.ctx.config_watcher = value
        print(value)

    def apply_watcher_interval(self, value):
        self.ctx.config_watcher_interval = value
        print(value)