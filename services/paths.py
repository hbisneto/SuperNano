# services/paths.py

from pathlib import Path
import platform
import os

APP_AUTHOR = "Bisneto"
APP_NAME = "SuperNanno"

def get_base_dir() -> Path:
    system = platform.system()
    if system == "Darwin":  # macOS
        return Path.home() / "Library" / "Application Support"
    elif system == "Windows":
        return Path(os.getenv("APPDATA", Path.home()))
    else:  # Linux
        return Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))

def get_app_dir() -> Path:
    return get_base_dir() / APP_AUTHOR / APP_NAME

def get_backups_dir() -> Path:
    return get_app_dir() / "Backups"

def get_rc_file():
    return get_app_dir() / ".supernannorc"

def get_config_dir() -> Path:
    return get_app_dir()

def get_cache_dir() -> Path:
    return get_app_dir() / "Cache"

def get_logs_dir() -> Path:
    return get_app_dir() / "Logs"