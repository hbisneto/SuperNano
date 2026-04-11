# services/config_manager.py

import json
from typing import Any, Dict
from services.paths import(
    get_config_dir, 
    get_rc_file
)
from services.rc_parser import parse_rc_file

DEFAULT_CONFIG = {
    "auto_backup": False,
    "config_watcher": True,
    "config_watcher_interval": 1,
    "restore_last_session": True,
    "tab_behavior": "indent",
    "indent_type": "spaces",
    "tab_size": 4
}

class ConfigManager:
    def __init__(self):
        self.config_path = get_config_dir() / "config.json"
        self.data = DEFAULT_CONFIG.copy()
        self.rc_path = get_rc_file()
        self._rc_mtime = None

        if self.config_path.exists():
            self._load()

        rc_config = parse_rc_file(get_rc_file())
        self.data.update(rc_config)

    def _load(self):
        try:
            with open(self.config_path, "r") as f:
                self.data.update(json.load(f))
        except Exception:
            pass

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)
    
    def reload_rc_if_changed(self):
        if not self.rc_path.exists():
            return False

        mtime = self.rc_path.stat().st_mtime

        if self._rc_mtime is None:
            self._rc_mtime = mtime
            return False

        if mtime != self._rc_mtime:
            self._rc_mtime = mtime

            rc_config = parse_rc_file(self.rc_path)
            self.data.update(rc_config)
            return True
        return False

    def save(self):
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.config_path, "w") as f:
            json.dump(self.data, f, indent=4)

    def set(self, key: str, value: Any, auto_save=True):
        self.data[key] = value

        if auto_save:
            try:
                self.save()
            except Exception:
                pass

        return True