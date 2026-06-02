# services/log_service.py

from datetime import datetime
from pathlib import Path


class LogService:
    """
    Interface pública de logging para o AppContext.

    Delega para o Logger estruturado (core.logger.Logger) que escreve
    entradas JSON com campos padronizados, correlation_id, stack trace,
    contexto do editor, etc.
    """

    def __init__(self, ctx):
        self.ctx = ctx

    # ─── Métodos públicos ─────────────────────────────────────────────

    def debug(
        self,
        msg: str,
        *,
        action: str = "",
        path=None,
        correlation_id: "str | None" = None,
        extra: "dict | None" = None,
    ) -> None:
        self._log("DEBUG", msg, action=action, path=path,
                  correlation_id=correlation_id, extra=extra)

    def info(
        self,
        msg: str,
        *,
        action: str = "",
        path=None,
        correlation_id: "str | None" = None,
        extra: "dict | None" = None,
    ) -> None:
        self._log("INFO", msg, action=action, path=path,
                  correlation_id=correlation_id, extra=extra)

    def warning(
        self,
        msg: str,
        *,
        action: str = "",
        path=None,
        correlation_id: "str | None" = None,
        extra: "dict | None" = None,
    ) -> None:
        self._log("WARN", msg, action=action, path=path,
                  correlation_id=correlation_id, extra=extra)

    def error(
        self,
        msg: str,
        *,
        action: str = "",
        path=None,
        exc: "Exception | None" = None,
        correlation_id: "str | None" = None,
        category: str = "",
        extra: "dict | None" = None,
    ) -> None:
        self._log("ERROR", msg, action=action, path=path, exc=exc,
                  correlation_id=correlation_id, category=category, extra=extra)

    def critical(
        self,
        msg: str,
        *,
        action: str = "",
        path=None,
        exc: "Exception | None" = None,
        correlation_id: "str | None" = None,
        category: str = "",
        extra: "dict | None" = None,
    ) -> None:
        self._log("CRITICAL", msg, action=action, path=path, exc=exc,
                  correlation_id=correlation_id, category=category, extra=extra)

    def get_recent_logs(self, lines: int = 30) -> str:
        """Retorna as últimas N linhas do log do dia."""
        return self.ctx.logger.get_recent_lines(lines)

    # ─── Privado ──────────────────────────────────────────────────────

    def _log(self, level: str, message: str, **kwargs) -> None:
        """Repassa para o logger estruturado injetando o ctx."""
        try:
            self.ctx.logger.write(level, message, ctx=self.ctx, **kwargs)
        except Exception:
            # LogService nunca pode crashar o editor
            pass
