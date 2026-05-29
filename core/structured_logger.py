# core/structured_logger.py

import asyncio
import json
import os
import platform
import sys
import threading
import traceback
import uuid
from datetime import datetime
from pathlib import Path


LEVELS: dict[str, int] = {
    "DEBUG":    10,
    "INFO":     20,
    "WARN":     30,
    "WARNING":  30,
    "ERROR":    40,
    "CRITICAL": 50,
}


class StructuredLogger:
    """
    Logger estruturado com saída JSON, correlation_id por operação,
    rastreamento de thread/task assíncrona e contexto do editor.

    É um componente "best-effort": qualquer falha interna é suprimida
    para nunca crashar o editor por problema de log.
    """

    def __init__(self, log_dir: Path, app_version: str = "unknown"):
        self.log_dir     = log_dir
        self.app_version = app_version
        self._os_info    = (
            f"{platform.system()} {platform.release()} ({platform.machine()})"
        )
        self._python_version = sys.version.split()[0]
        self._ensure_dir()

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    def new_correlation_id(self) -> str:
        """Gera um correlation_id único de 8 hex chars."""
        return uuid.uuid4().hex[:8]

    def write(
        self,
        level: str,
        message: str,
        *,
        action: str = "",
        path: "str | Path | None" = None,
        exc: "Exception | None" = None,
        correlation_id: "str | None" = None,
        event_origin: str = "",
        category: str = "",
        ctx=None,
        extra: "dict | None" = None,
    ) -> None:
        """
        Escreve uma entrada de log estruturada em JSON.

        Parâmetros
        ----------
        level           : DEBUG / INFO / WARN / ERROR / CRITICAL
        message         : Mensagem principal legível
        action          : Ação semântica (ex: FILE_SAVE, CONFIG_LOAD)
        path            : Caminho do arquivo afetado, se aplicável
        exc             : Objeto de exceção (se houver)
        correlation_id  : ID de correlação para agrupar logs da mesma operação
        event_origin    : Ação do usuário que disparou o evento (ex: ctrl_s)
        category        : Categoria para triagem de issues (ex: FILE_PERMISSION_ERROR)
        ctx             : AppContext (opcional, para enriquecer com estado do editor)
        extra           : Dados adicionais arbitrários
        """
        try:
            self._write_internal(
                level=level,
                message=message,
                action=action,
                path=path,
                exc=exc,
                correlation_id=correlation_id,
                event_origin=event_origin,
                category=category,
                ctx=ctx,
                extra=extra,
            )
        except Exception:
            # Log é best-effort. Nunca pode crashar o editor.
            pass

    def get_recent_lines(self, n: int = 30) -> str:
        """Retorna as últimas N linhas do log do dia atual."""
        try:
            log_file = self._get_log_file()
            if not log_file.exists():
                return "No logs for today."
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            return "".join(lines[-n:])
        except OSError as e:
            return f"Could not read logs: {e}"
        except Exception as e:
            return f"Unexpected error reading logs: {e}"

    # ─────────────────────────────────────────────
    # Internal helpers
    # ─────────────────────────────────────────────

    def _ensure_dir(self) -> None:
        try:
            self.log_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass  # Se não puder criar o dir de log, silencia — log é best-effort

    def _get_log_file(self) -> Path:
        date = datetime.now().strftime("%Y-%m-%d")
        return self.log_dir / f"supernanno_{date}.log"

    def _write_internal(
        self,
        *,
        level: str,
        message: str,
        action: str,
        path: "str | Path | None",
        exc: "Exception | None",
        correlation_id: "str | None",
        event_origin: str,
        category: str,
        ctx,
        extra: "dict | None",
    ) -> None:
        level_upper = level.upper()
        now         = datetime.now()

        # Informações de exceção
        exc_type    = None
        exc_message = None
        exc_tb      = None
        if exc is not None:
            exc_type    = type(exc).__name__
            exc_message = str(exc)
            exc_tb      = traceback.format_exc()

        # Detecta task assíncrona atual
        task_name = None
        try:
            task = asyncio.current_task()
            if task:
                task_name = task.get_name()
        except RuntimeError:
            pass

        # Contexto do editor (capturado defensivamente)
        editor_state: dict  = {}
        session_state: dict = {}
        if ctx is not None:
            try:
                editor_state = {
                    "current_file": str(ctx.current_path) if ctx.current_path else None,
                    "is_dirty":     bool(ctx.is_dirty),
                    "read_only":    bool(ctx.read_only),
                    "encoding":     getattr(ctx, "encoding", "UTF-8"),
                    "eol":          getattr(ctx, "eol", "LF"),
                    "word_count":   getattr(ctx, "word_count", 0),
                    "char_count":   getattr(ctx, "char_count", 0),
                }
            except Exception:
                editor_state = {}

            try:
                session_state = {
                    "restore_session": bool(getattr(ctx, "restore_session", False)),
                    "backup_enabled":  bool(getattr(ctx, "backup_enabled", False)),
                    "config_watcher":  bool(getattr(ctx, "config_watcher", False)),
                }
            except Exception:
                session_state = {}

        entry: dict = {
            "timestamp":      now.isoformat(),
            "level":          level_upper,
            "level_num":      LEVELS.get(level_upper, 0),
            "correlation_id": correlation_id or "",
            "message":        message,
            "action":         action,
            "path":           str(path) if path else None,
            "exc_type":       exc_type,
            "exc_message":    exc_message,
            "exc_traceback":  exc_tb,
            "os":             self._os_info,
            "python_version": self._python_version,
            "app_version":    self.app_version,
            "editor_state":   editor_state,
            "session_state":  session_state,
            "thread_id":      threading.current_thread().name,
            "task_name":      task_name,
            "event_origin":   event_origin,
            "category":       category,
        }

        if extra:
            entry["extra"] = extra

        line = json.dumps(entry, ensure_ascii=False, default=str)

        try:
            log_file = self._get_log_file()
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(line + "\n")
        except OSError:
            pass  # Log é best-effort — nunca crashar o editor por falha de log
