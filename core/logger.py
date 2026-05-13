# core/logger.py

from pathlib import Path
from datetime import datetime

class Logger:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def write(self, message: str):
        file = self._get_log_file()

        with open(file, "a", encoding="utf-8") as f:
            f.write(message + "\n")

    def _get_log_file(self) -> Path:
        date = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"log_{date}.log"