import json
from services.paths import get_config_dir

class SessionManager:
    def __init__(self, create_if_missing: bool = False):
        self.session_path = get_config_dir() / "session.json"
        self._session = {
            "last_file": None,
            "recent_files": []
        }

        if self.session_path.exists():
            self.load()

        elif create_if_missing:
            self.save()

    def load(self):
        try:
            with open(self.session_path, "r", encoding="utf-8") as f:
                self._session.update(json.load(f))
        except Exception:
            pass

    def save(self):
        try:
            self.session_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.session_path, "w", encoding="utf-8") as f:
                json.dump(self._session, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def get_last_file(self):
        return self._session.get("last_file")

    def set_last_file(self, path: str):
        self._session["last_file"] = path
        self.save()

    def add_recent_file(self, path: str):
        if path not in self._session["recent_files"]:
            self._session["recent_files"].insert(0, path)

        self._session["recent_files"] = self._session["recent_files"][:10]
        self.save()

    def get_recent_files(self):
        return self._session.get("recent_files", [])