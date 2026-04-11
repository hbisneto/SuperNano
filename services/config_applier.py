# services/config_applier.py

class ConfigApplier:
    def __init__(self, app):
        self.app = app

        self.handlers = {
            "auto_backup": self.apply_auto_backup,
            "config_watcher": self.apply_watcher,
            "config_watcher_interval": self.apply_watcher_interval,
            "tab_size": self.apply_tab_size,
        }

    def apply(self, config):
        for key, handler in self.handlers.items():
            if key in config:
                handler(config[key])

    ###==================== HANDLERS ====================###

    def apply_auto_backup(self, value):
        self.app.ctx.auto_backup_enabled = value

    def apply_tab_size(self, value):
        editor = self.app.get_editor()
        editor.tab_behavior = "indent"
        editor.indent_type = "spaces"
        editor.indent_width = value
        editor.refresh()

    def apply_watcher(self, value):
        self.app.config_watcher = value

    def apply_watcher_interval(self, value):
        self.app.config_watcher_interval = value

# SuperNanno configuration

# set tab_size 4
# set tab_behavior indent
# set indent_type spaces