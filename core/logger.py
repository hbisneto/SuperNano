# core/logger.py
from pathlib import Path
from datetime import datetime
import json
from typing import Any, Dict

class Logger:
    """
    Responsabilidade: Gerenciar escrita de logs em arquivos diários.
    Formato JSON para facilitar parsing futuro.
    """

    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self._current_date = None
        self._current_file: Path | None = None

    def _get_log_file(self) -> Path:
        today = datetime.now().strftime("%Y-%m-%d")
        if today != self._current_date or not self._current_file:
            self._current_date = today
            self._current_file = self.log_dir / f"supernanno_{today}.log"
        return self._current_file

    def write(self, message: str, level: str = "INFO", extra: Dict[str, Any] | None = None):
        """Escreve log estruturado em JSON."""
        file_path = self._get_log_file()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        log_entry = {
            "timestamp": timestamp,
            "level": level.upper(),
            "message": message,
        }

        if extra:
            log_entry.update(extra)

        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        except Exception:
            pass  # Fail silently to avoid error loops

    def write_raw(self, text: str):
        """Escreve texto puro (para logs legíveis)."""
        file_path = self._get_log_file()
        try:
            with open(file_path, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {text}\n")
        except Exception:
            pass