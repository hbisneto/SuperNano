# services/log_service.py

from datetime import datetime
from pathlib import Path

class LogService:
    def __init__(self, ctx):
        self.ctx = ctx

    def info(self, message: str):
        self._log("INFO", message)

    def warning(self, message: str):
        self._log("WARN", message)

    def error(self, message: str):
        self._log("ERROR", message)

    def debug(self, message: str):
        self._log("DEBUG", message)

    def _log(self, level: str, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        path = self.ctx.current_path or "NoFile"
        formatted = f"[{timestamp}] [{level}] [{path}] {message}"
        self.ctx.logger.write(formatted)
    
    def get_recent_logs(self, lines=20):
        log_file = self.ctx.logger._get_log_file()

        if not log_file.exists():
            return "No logs"

        with open(log_file, "r", encoding="utf-8") as f:
            content = f.readlines()

        return "".join(content[-lines:])