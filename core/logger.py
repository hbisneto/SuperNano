# core/logger.py
#
# Mantido para compatibilidade com imports existentes.
# Internamente delega para StructuredLogger.

from pathlib import Path
from datetime import datetime
from core.structured_logger import StructuredLogger


class Logger:
    """
    Wrapper de compatibilidade sobre StructuredLogger.

    Preserva a API original `Logger(log_dir).write(message)` enquanto
    expõe a interface nova `write(level, message, **kwargs)` usada pelo
    LogService e ErrorService modernizados.
    """

    def __init__(self, log_dir: Path, app_version: str = "unknown"):
        self._structured = StructuredLogger(log_dir, app_version=app_version)
        self.log_dir     = log_dir

    # ─── API NOVA (usada por LogService e ErrorService) ───────────────

    def write(
        self,
        level_or_message: str,
        message: str = "",
        *,
        action: str = "",
        path=None,
        exc=None,
        correlation_id=None,
        event_origin: str = "",
        category: str = "",
        ctx=None,
        extra=None,
    ) -> None:
        """
        API unificada — aceita duas formas de chamada:

        Nova:   write("ERROR", "msg", action=..., exc=..., ctx=...)
        Antiga: write("texto simples")  → gravado como INFO
        """
        # Detecta chamada legada (argumento único sem nível)
        known_levels = {"DEBUG", "INFO", "WARN", "WARNING", "ERROR", "CRITICAL"}

        if level_or_message.upper() in known_levels and message:
            # Nova forma
            level   = level_or_message
            msg     = message
        else:
            # Forma legada: write("texto") — grava como INFO
            level   = "INFO"
            msg     = level_or_message

        self._structured.write(
            level,
            msg,
            action=action,
            path=path,
            exc=exc,
            correlation_id=correlation_id,
            event_origin=event_origin,
            category=category,
            ctx=ctx,
            extra=extra,
        )

    # ─── Helpers diretos ──────────────────────────────────────────────

    def new_correlation_id(self) -> str:
        return self._structured.new_correlation_id()

    def get_recent_lines(self, n: int = 30) -> str:
        return self._structured.get_recent_lines(n)

    # ─── Compatibilidade com IssueService (referencia _get_log_file) ─

    def _get_log_file(self):
        return self._structured._get_log_file()
