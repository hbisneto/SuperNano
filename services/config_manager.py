# services/config_manager.py

from pathlib import Path
import json
from typing import Any, Dict, Optional

class ConfigManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = Path(config_path)
        self._config: Dict = {}
        self.load()

    def load(self) -> bool:
        """Carrega o config.json ou cria um default se não existir."""
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config = json.load(f)
                return True
            except Exception:
                self._config = self._get_default_config()
                self.save()
                return False
        else:
            self._config = self._get_default_config()
            self.save()
            return True

    def save(self) -> bool:
        """Salva o config atual no arquivo."""
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self._config, f, indent=4, ensure_ascii=False)
            return True
        except Exception:
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Pega um valor usando notação de ponto (ex: 'session.last_opened_file')"""
        keys = key.split('.')
        data = self._config
        for k in keys:
            if isinstance(data, dict):
                data = data.get(k, default)
            else:
                return default
        return data if data is not None else default

    def set(self, key: str, value: Any) -> bool:
        """Define um valor usando notação de ponto"""
        keys = key.split('.')
        data = self._config
        for i, k in enumerate(keys[:-1]):
            if k not in data or not isinstance(data[k], dict):
                data[k] = {}
            data = data[k]
        data[keys[-1]] = value
        return self.save()

    def _get_default_config(self) -> Dict:
        """Retorna a estrutura padrão atualizada"""
        return {
            "settings": {
                "startup": {
                    "default_save_location": "",
                    "restore_last_session": True
                },
                "session": {
                    "last_opened_file": "",
                    "recent_files": [],
                    "auto_save": False,
                    "auto_save_interval": 60
                },
                "editor": {
                    "tab_size": 4,
                    "use_spaces": True,
                    "auto_indent": True,
                    "word_wrap": True,
                    "highlight_current_line": True
                },
                "ui": {
                    "line_numbers": True,
                    "theme": "dark",
                    "status_bar": True
                },
                "search": {
                    "case_sensitive": False,
                    "use_regex": False,
                    "highlight_all_matches": True
                }
            }
        }