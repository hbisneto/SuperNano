# services/error_service.py

import hashlib
import traceback
import uuid
from datetime import datetime

# ─── Mapeamento de tipo de exceção → categoria semântica ──────────────
ERROR_CATEGORIES: dict[str, str] = {
    "PermissionError":        "FILE_PERMISSION_ERROR",
    "FileNotFoundError":      "FILE_NOT_FOUND_ERROR",
    "IsADirectoryError":      "FILE_IS_DIRECTORY_ERROR",
    "UnicodeDecodeError":     "FILE_ENCODING_ERROR",
    "UnicodeError":           "FILE_ENCODING_ERROR",
    "OSError":                "FILESYSTEM_ERROR",
    "JSONDecodeError":        "CONFIG_PARSE_ERROR",
    "json.JSONDecodeError":   "CONFIG_PARSE_ERROR",
    "ValueError":             "VALIDATION_ERROR",
    "AttributeError":         "UI_STATE_ERROR",
    "TypeError":              "UI_STATE_ERROR",
    "RuntimeError":           "RUNTIME_ERROR",
    "asyncio.CancelledError": "ASYNC_CANCELLED",
    "CancelledError":         "ASYNC_CANCELLED",
    "TimeoutError":           "TIMEOUT_ERROR",
    "KeyError":               "VALIDATION_ERROR",
    "IndexError":             "VALIDATION_ERROR",
}

# Mapeamento categoria → labels do GitHub Issues
CATEGORY_LABELS: dict[str, str] = {
    "FILE_PERMISSION_ERROR":   "bug,permissions",
    "FILE_NOT_FOUND_ERROR":    "bug,file-io",
    "FILE_IS_DIRECTORY_ERROR": "bug,file-io",
    "FILE_ENCODING_ERROR":     "bug,encoding",
    "FILESYSTEM_ERROR":        "bug,file-io",
    "CONFIG_PARSE_ERROR":      "bug,config",
    "VALIDATION_ERROR":        "bug",
    "UI_STATE_ERROR":          "bug,ui",
    "RUNTIME_ERROR":           "bug",
    "ASYNC_CANCELLED":         "bug,async",
    "TIMEOUT_ERROR":           "bug,async",
    "UNCLASSIFIED_ERROR":      "bug,needs-triage",
}


def _make_fingerprint(exc_type: str, tb_str: str) -> str:
    """Hash MD5 determinístico para deduplicação de issues no GitHub."""
    key = f"{exc_type}:{tb_str[:300]}"
    return hashlib.md5(key.encode()).hexdigest()[:12]


class ErrorService:
    """
    Serviço central de tratamento de erros.

    Responsabilidades:
    - Gerar correlation_id único por erro
    - Categorizar a exceção semanticamente
    - Registrar stack trace completo no log estruturado
    - Persistir estado da última exceção (para CTRL+X / IssueService)
    - Notificar o usuário via status bar e notify()
    """

    def __init__(self, ctx):
        self.ctx = ctx

    def handle(
        self,
        exc: Exception,
        *,
        action: str = "",
        path=None,
        event_origin: str = "",
        extra: "dict | None" = None,
    ) -> str:
        """
        Registra uma exceção com contexto completo.

        Parâmetros
        ----------
        exc          : A exceção capturada
        action       : Ação semântica que originou o erro (ex: FILE_SAVE)
        path         : Path do arquivo envolvido, se aplicável
        event_origin : Ação do usuário (ex: ctrl_s, sidebar_click)
        extra        : Dados adicionais para o log

        Retorna
        -------
        correlation_id : str  — ID de 8 hex chars para rastreamento
        """
        correlation_id = uuid.uuid4().hex[:8]
        exc_type_name  = type(exc).__name__
        category       = ERROR_CATEGORIES.get(exc_type_name, "UNCLASSIFIED_ERROR")
        tb_str         = traceback.format_exc()
        fingerprint    = _make_fingerprint(exc_type_name, tb_str)
        github_labels  = CATEGORY_LABELS.get(category, "bug,needs-triage")

        # ── Enriquece o extra com metadados de diagnóstico ──────────
        full_extra = {
            "fingerprint":    fingerprint,
            "github_labels":  github_labels,
            **(extra or {}),
        }

        # ── Registra no log estruturado ──────────────────────────────
        try:
            self.ctx.logger.write(
                "ERROR",
                f"[{correlation_id}] {exc_type_name}: {exc}",
                action=action or exc_type_name,
                path=path,
                exc=exc,
                correlation_id=correlation_id,
                event_origin=event_origin,
                category=category,
                ctx=self.ctx,
                extra=full_extra,
            )
        except Exception:
            pass  # Logger nunca pode causar crash secundário

        # ── Persiste estado para IssueService ─────────────────────────
        self.ctx.last_exception      = tb_str
        self.ctx.last_exception_type = exc_type_name
        self.ctx.last_exception_time = datetime.now()
        self.ctx.last_correlation_id = correlation_id
        self.ctx.last_error_category = category
        self.ctx.last_error_labels   = github_labels
        self.ctx.last_fingerprint    = fingerprint

        # ── Atualiza status bar ───────────────────────────────────────
        if not self.ctx.status.is_locked():
            self.ctx.status.error(
                f"[{correlation_id}] {exc_type_name} — press CTRL+X to report"
            )

        # ── Notificação visual (best-effort) ──────────────────────────
        try:
            self.ctx.app.notify(
                f"Error [{correlation_id}]: {exc_type_name}. Press CTRL+X to report.",
                title="Error",
                severity="error",
                timeout=10,
            )
        except Exception:
            # notify() nunca pode causar crash secundário
            pass

        return correlation_id
