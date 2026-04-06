# core/status.py

from datetime import datetime
class StatusService:
    def __init__(self, app, debug=False):
        self.app = app
        self.debug_mode = debug
        self.history = []

    ###==================== CORE ====================###

    def set(self, text, delay=None, next_text=None, status_type="normal"):
        self._log(text, status_type)

        self.app.set_status(text, delay, next_text, status_type)

    ###==================== LOG SYSTEM ====================###

    def _log(self, text, level):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": text,
        }

        self.history.append(entry)

        if self.debug_mode:
            print(f"[{entry['time']}] [{level.upper()}] {text}")

    ###==================== HELPERS ====================###

    def info(self, text, **kwargs):
        self.set(text, status_type="info", **kwargs)

    def success(self, text, **kwargs):
        self.set(text, status_type="success", **kwargs)

    def warning(self, text, **kwargs):
        self.set(text, status_type="warning", **kwargs)

    def error(self, text, **kwargs):
        self.set(text, status_type="error", **kwargs)

    def debug(self, text):
        if self.debug_mode:
            self._log(text, "debug")

    ###==================== HISTORY ====================###
    
    def get_last(self, n=10):
        return self.history[-n:]

    def clear_history(self):
        self.history.clear()