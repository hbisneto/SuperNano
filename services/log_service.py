# services/log_service.py
from datetime import datetime
from typing import Any, Dict

class LogService:
    """
    Camada de serviço de alto nível para logging.
    Centraliza logs + integração com Status e AppContext.
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def _log(self, level: str, message: str, extra: Dict[str, Any] | None = None):
        path = str(self.ctx.current_path or "NoFile")
        extra_data = {"file": path, **(extra or {})}
        self.ctx.logger.write(message, level, extra_data)

    def info(self, message: str, extra: Dict = None):
        self._log("INFO", message, extra)
        if not self.ctx.status.is_locked():
            self.ctx.status.info(message)

    def warning(self, message: str, extra: Dict = None):
        self._log("WARN", message, extra)
        self.ctx.status.warning(message)

    def error(self, message: str, extra: Dict = None):
        self._log("ERROR", message, extra)
        self.ctx.status.error(message)

    def debug(self, message: str, extra: Dict = None):
        if getattr(self.ctx, "debug_mode", False):
            self._log("DEBUG", message, extra)

    def exception(self, exc: Exception, context: str | None = None):
        """Método principal para capturar exceções."""
        import traceback
        trace = traceback.format_exc()
        msg = context or f"{type(exc).__name__}: {exc}"

        self._log("ERROR", msg, {
            "exception_type": type(exc).__name__,
            "traceback": trace
        })

        if not self.ctx.status.is_locked():
            self.ctx.status.error(f"{type(exc).__name__} occurred (check logs)")

    def get_recent_logs(self, lines: int = 50) -> str:
        """Retorna últimas linhas dos logs (útil para debug)."""
        try:
            log_file = self.ctx.logger._get_log_file()
            if not log_file.exists():
                return "No logs available yet."

            with open(log_file, "r", encoding="utf-8") as f:
                content = f.readlines()
            return "".join(content[-lines:])
        except Exception as e:
            return f"Failed to read logs: {e}"