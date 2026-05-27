# services/issue_service.py
#
#
# Arquitetura:
#   LogExcerptFormatter   → Converte JSON logs em texto humano legível
#   IssueReportBuilder    → Monta o body compacto da issue (com truncamento)
#   DiagnosticBundleService → Gera o ZIP de diagnóstico completo
#   GitHubIssueFormatter  → Formata título/labels para o GitHub
#   GitHubReportProvider  → Abre a URL no browser (substituível por testes)
#   DiagnosticContext     → Coleta estado do app no momento do report
#   IssueTemplate         → Renderiza template Markdown compacto
#   IssueService          → API pública — único ponto de entrada do app
#
# Garantias:
#   - URL nunca excede MAX_GITHUB_BODY caracteres no body
#   - JSON bruto nunca vai na URL — apenas texto humano legível
#   - Bundle gerado best-effort — falha silenciosa, nunca crasha o editor
#   - Todas as exceções são absorvidas internamente

import io
import json
import os
import platform
import shutil
import sys
import tempfile
import traceback
import webbrowser
import zipfile
from datetime import datetime
from pathlib import Path
from urllib.parse import quote, urlencode

from core.__version__ import VERSION
from services.paths import get_app_dir, get_logs_dir

# ──────────────────────────────────────────────────────────────────────────────
# Constantes
# ──────────────────────────────────────────────────────────────────────────────

GITHUB_REPO   = "hbisneto/SuperNanno"
GITHUB_ISSUES = f"https://github.com/{GITHUB_REPO}/issues/new"
ISSUE_LABEL   = "bug"

# Limite máximo de caracteres do body enviado na query string.
# GitHub suporta até ~8 000 chars na URL, mas browsers têm limites menores.
# 4 000 chars é seguro para todos os cenários conhecidos.
MAX_GITHUB_BODY = 4_000

# Quantas linhas de log recuperar para o excerpt da issue
LOG_EXCERPT_LINES = 30

# Quantas entradas do excerpt incluir no body da issue
LOG_EXCERPT_MAX_ENTRIES = 8

# Diretório onde os bundles são salvos
ISSUES_DIR_NAME = "Issues"


# ──────────────────────────────────────────────────────────────────────────────
# LogExcerptFormatter
# ──────────────────────────────────────────────────────────────────────────────

class LogExcerptFormatter:
    """
    Converte linhas de log JSON estruturado em texto humano legível.

    Entrada (cada linha):
        {"level":"ERROR","action":"FILE_SAVE","exc_type":"PermissionError",
         "message":"...","correlation_id":"abc12345","path":"/tmp/x.py",...}

    Saída:
        [ERROR] FILE_SAVE
        Path: /tmp/x.py
        Exception: PermissionError
        Message: Permission denied
        Correlation ID: abc12345
    """

    # Campos que devem ser incluídos na saída legível e seus rótulos
    _FIELDS: list[tuple[str, str]] = [
        ("path",           "Path"),
        ("exc_type",       "Exception"),
        ("exc_message",    "Message"),
        ("correlation_id", "Correlation ID"),
        ("event_origin",   "Triggered By"),
        ("category",       "Category"),
    ]

    def format_line(self, raw_line: str) -> str:
        """
        Formata uma única linha JSON de log em texto legível.

        Se a linha não for JSON válido, devolve a linha crua truncada.
        Nunca levanta exceção.
        """
        try:
            entry: dict = json.loads(raw_line.strip())
        except (json.JSONDecodeError, ValueError):
            # Linha não-JSON — devolve crua truncada
            return raw_line[:200].strip()
        except Exception:
            return ""

        try:
            level  = entry.get("level",  "INFO").upper()
            action = entry.get("action", "")
            ts     = entry.get("timestamp", "")

            # Linha de cabeçalho: [LEVEL] ACTION  (timestamp opcional)
            header = f"[{level}] {action}" if action else f"[{level}]"
            if ts:
                # Extrai só a hora (HH:MM:SS) para compactar
                time_part = ts[11:19] if len(ts) >= 19 else ts
                header = f"{header}  ({time_part})"

            lines = [header]

            for field_key, field_label in self._FIELDS:
                value = entry.get(field_key)
                if value:
                    lines.append(f"  {field_label}: {value}")

            return "\n".join(lines)

        except Exception:
            return raw_line[:200].strip()

    def format_excerpt(self, raw_log_text: str, max_entries: int = LOG_EXCERPT_MAX_ENTRIES) -> str:
        """
        Formata as últimas N entradas de log como texto legível.

        Parâmetros
        ----------
        raw_log_text : Saída bruta de logger.get_recent_lines()
        max_entries  : Máximo de entradas a incluir

        Retorna
        -------
        Texto multi-linha legível por humanos, não JSON bruto.
        """
        if not raw_log_text or raw_log_text.startswith("No logs") or raw_log_text.startswith("Could not"):
            return raw_log_text or "No recent logs available."

        lines = [l for l in raw_log_text.splitlines() if l.strip()]
        # Pega as últimas max_entries linhas
        selected = lines[-max_entries:] if len(lines) > max_entries else lines

        formatted_entries: list[str] = []
        for raw_line in selected:
            formatted = self.format_line(raw_line)
            if formatted:
                formatted_entries.append(formatted)

        if not formatted_entries:
            return "No parseable log entries found."

        return "\n---\n".join(formatted_entries)


# ──────────────────────────────────────────────────────────────────────────────
# DiagnosticContext
# ──────────────────────────────────────────────────────────────────────────────

class DiagnosticContext:
    """
    Captura o estado completo do app no momento do report.

    Todos os acessos são defensivos — nunca levanta exceção.
    """

    def __init__(self, ctx):
        formatter = LogExcerptFormatter()

        self.traceback       = ctx.last_exception        or "No traceback available."
        self.exc_type        = ctx.last_exception_type   or "Unknown"
        self.exc_time        = ctx.last_exception_time   or datetime.now()
        self.correlation_id  = getattr(ctx, "last_correlation_id", "") or ""
        self.category        = getattr(ctx, "last_error_category",  "UNCLASSIFIED_ERROR")
        self.github_labels   = getattr(ctx, "last_error_labels",    ISSUE_LABEL)
        self.fingerprint     = getattr(ctx, "last_fingerprint",     "") or ""

        # Log em formato JSON bruto (para bundle)
        self.raw_recent_logs = self._get_raw_logs(ctx)

        # Log em formato humano legível (para URL da issue)
        self.log_excerpt = formatter.format_excerpt(self.raw_recent_logs)

        self.os_info         = self._get_os()
        self.python_ver      = sys.version.split()[0]
        self.app_version     = VERSION
        self.file_path       = str(ctx.current_path) if ctx.current_path else "No file open"
        self.encoding        = getattr(ctx, "encoding",   "UTF-8")
        self.cursor          = self._get_cursor(ctx)
        self.word_count      = getattr(ctx, "word_count", 0)
        self.char_count      = getattr(ctx, "char_count", 0)
        self.file_size       = ctx.format_size(getattr(ctx, "file_size", 0))
        self.eol             = getattr(ctx, "eol",        "LF")
        self.read_only       = getattr(ctx, "read_only",  False)
        self.restore_session = getattr(ctx, "restore_session", False)
        self.backup_enabled  = getattr(ctx, "backup_enabled",  False)

    @staticmethod
    def _get_raw_logs(ctx) -> str:
        try:
            return ctx.logs.get_recent_logs(lines=LOG_EXCERPT_LINES)
        except Exception as e:
            try:
                ctx.logs.debug(
                    f"(DiagnosticContext): Could not retrieve recent logs — {e}",
                    action="DIAG_GET_LOGS",
                )
            except Exception:
                pass
            return f"Could not retrieve logs: {e}"

    @staticmethod
    def _get_os() -> str:
        return f"{platform.system()} {platform.release()} ({platform.machine()})"

    @staticmethod
    def _get_cursor(ctx) -> str:
        try:
            row, col = ctx.editor.cursor_location
            return f"Ln {row + 1}, Col {col + 1}"
        except Exception as e:
            try:
                ctx.logs.debug(
                    f"(DiagnosticContext): Could not read cursor location — {e}",
                    action="DIAG_GET_CURSOR",
                )
            except Exception:
                pass
            return "N/A"


# ──────────────────────────────────────────────────────────────────────────────
# IssueReportBuilder
# ──────────────────────────────────────────────────────────────────────────────

class IssueReportBuilder:
    """
    Monta o body compacto da issue para envio via URL.

    Regras:
    - Nunca inclui JSON bruto
    - Usa excerpt humano legível limitado
    - Trunca automaticamente ao atingir MAX_GITHUB_BODY
    - Inclui instrução para anexar o bundle
    """

    def build_body(
        self,
        diag: DiagnosticContext,
        bundle_path: "Path | None" = None,
        max_chars: int = MAX_GITHUB_BODY,
    ) -> str:
        """
        Monta o body da issue respeitando o limite de caracteres.

        Parâmetros
        ----------
        diag        : Contexto de diagnóstico capturado
        bundle_path : Caminho do bundle ZIP gerado (pode ser None)
        max_chars   : Limite máximo de caracteres para o body

        Retorna
        -------
        String Markdown pronta para ser usada na URL do GitHub.
        Sempre truncada para max_chars.
        """
        cid_line = (
            f"**Correlation ID:** `{diag.correlation_id}`  \n"
            f"**Fingerprint:** `{diag.fingerprint}`  \n"
            f"**Category:** `{diag.category}`"
        ) if diag.correlation_id else f"**Category:** `{diag.category}`"

        # Traceback resumido: apenas primeiras 20 linhas
        tb_lines   = diag.traceback.splitlines()
        tb_summary = "\n".join(tb_lines[:20])
        if len(tb_lines) > 20:
            tb_summary += f"\n... ({len(tb_lines) - 20} more lines in bundle)"

        # Instrução de bundle
        if bundle_path:
            bundle_instruction = (
                f"\n---\n\n"
                f"### 📎 Diagnostic Bundle\n\n"
                f"A diagnostic bundle was generated automatically.\n\n"
                f"**Please attach this file to this GitHub issue:**\n\n"
                f"```\n{bundle_path}\n```\n\n"
                f"The bundle contains: full logs, config files, "
                f"traceback, and environment info.\n"
            )
        else:
            bundle_instruction = (
                "\n---\n\n"
                "### 📎 Diagnostic Bundle\n\n"
                "Bundle generation was unavailable. "
                "Please attach logs manually if possible.\n"
            )

        body = f"""\
## Bug Report — SuperNanno {diag.app_version}

> Generated automatically. Please review and add context before submitting.

{cid_line}

---

### Environment

| Field      | Value |
|------------|-------|
| SuperNanno | {diag.app_version} |
| OS         | {diag.os_info} |
| Python     | {diag.python_ver} |
| Time       | {diag.exc_time.strftime("%Y-%m-%d %H:%M:%S")} |

---

### Editor State

| Field      | Value |
|------------|-------|
| File       | {diag.file_path} |
| Encoding   | {diag.encoding} |
| EOL        | {diag.eol} |
| Cursor     | {diag.cursor} |
| Read-Only  | {diag.read_only} |

---

### Exception

**Type:** `{diag.exc_type}`

```
{tb_summary}
```

---

### Recent Log Excerpt

```
{diag.log_excerpt}
```
{bundle_instruction}
---

### Steps to Reproduce

<!-- Describe what you were doing when this error occurred -->

1.
2.
3.

### Expected Behavior

<!-- What did you expect? -->

### Actual Behavior

<!-- What happened? -->
"""

        return self._truncate(body, max_chars)

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        """
        Trunca o body ao limite de caracteres, adicionando aviso de truncamento.
        Preserva a estrutura Markdown na medida do possível.
        """
        if len(text) <= max_chars:
            return text

        truncation_notice = (
            "\n\n---\n"
            "_⚠️ Body truncated to fit GitHub URL limits. "
            "Full details are in the diagnostic bundle._\n"
        )
        # Reserva espaço para o aviso de truncamento
        available = max_chars - len(truncation_notice)
        return text[:available] + truncation_notice


# ──────────────────────────────────────────────────────────────────────────────
# DiagnosticBundleService
# ──────────────────────────────────────────────────────────────────────────────

class DiagnosticBundleService:
    """
    Gera um ZIP de diagnóstico completo contendo:
        logs/    → logs JSON completos do dia atual
        config/  → config.json e .supernannorc
        system/  → info de ambiente (Python, SO, versão do app)
        crash/   → traceback completo e estado do editor

    Filosofia:
    - Totalmente best-effort: nunca levanta exceção
    - Cada seção do bundle é independente: falha em uma não cancela as demais
    - Salvo em ~/Library/Application Support/Bisneto/SuperNanno/Issues/
      (ou equivalente de plataforma via get_app_dir())
    """

    def __init__(self):
        self._issues_dir: "Path | None" = None

    def _get_issues_dir(self) -> Path:
        """Retorna (e cria se necessário) o diretório de issues."""
        if self._issues_dir is None:
            self._issues_dir = get_app_dir() / ISSUES_DIR_NAME
        try:
            self._issues_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass
        return self._issues_dir

    def generate(self, diag: DiagnosticContext, ctx) -> "Path | None":
        """
        Gera o bundle ZIP de diagnóstico.

        Parâmetros
        ----------
        diag : DiagnosticContext já coletado
        ctx  : AppContext (para acesso ao logger e config)

        Retorna
        -------
        Path do arquivo ZIP gerado, ou None em caso de falha total.
        """
        timestamp  = datetime.now().strftime("%Y%m%d_%H%M%S")
        cid_suffix = f"_{diag.correlation_id}" if diag.correlation_id else ""
        zip_name   = f"issue_bundle{cid_suffix}_{timestamp}.zip"
        issues_dir = self._get_issues_dir()
        zip_path   = issues_dir / zip_name

        # Cria ZIP em arquivo temporário primeiro (atomic write)
        tmp_path: "Path | None" = None
        try:
            tmp_fd, tmp_str = tempfile.mkstemp(suffix=".zip", dir=str(issues_dir))
            os.close(tmp_fd)
            tmp_path = Path(tmp_str)

            with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
                self._add_logs(zf, ctx, diag)
                self._add_config(zf, ctx)
                self._add_system_info(zf, diag)
                self._add_crash_info(zf, diag)

            # Rename atômico
            tmp_path.replace(zip_path)
            return zip_path

        except Exception as e:
            # Limpa arquivo temporário em caso de falha
            if tmp_path is not None:
                try:
                    tmp_path.unlink(missing_ok=True)
                except Exception:
                    pass

            # Loga o erro de geração do bundle (best-effort)
            try:
                ctx.logs.warning(
                    f"(Bundle): Could not generate diagnostic bundle — {e}",
                    action="BUNDLE_GENERATE_FAILED",
                    extra={"traceback": traceback.format_exc()},
                )
            except Exception:
                pass

            return None

    # ── Seções do bundle ──────────────────────────────────────────────

    def _add_logs(self, zf: zipfile.ZipFile, ctx, diag: DiagnosticContext) -> None:
        """Adiciona os logs completos do dia atual."""
        try:
            log_file = ctx.logger._get_log_file()
            if log_file.exists():
                zf.write(log_file, arcname=f"logs/{log_file.name}")
            else:
                zf.writestr("logs/no_log_today.txt", "No log file found for today.")

        except Exception as e:
            try:
                zf.writestr("logs/error.txt", f"Could not include logs: {e}\n{traceback.format_exc()}")
            except Exception:
                pass

        # Também inclui o excerpt formatado (para leitura rápida)
        try:
            zf.writestr("logs/recent_excerpt.txt", diag.raw_recent_logs or "No recent logs.")
        except Exception:
            pass

    def _add_config(self, zf: zipfile.ZipFile, ctx) -> None:
        """Adiciona config.json e .supernannorc."""
        # config.json
        try:
            config_path = ctx.config.config_path
            if config_path.exists():
                zf.write(config_path, arcname="config/config.json")
            else:
                # Serializa o estado em memória
                config_data = json.dumps(ctx.config.data, indent=4, ensure_ascii=False, default=str)
                zf.writestr("config/config_in_memory.json", config_data)
        except Exception as e:
            try:
                zf.writestr("config/config_error.txt", f"Could not include config.json: {e}")
            except Exception:
                pass

        # .supernannorc
        try:
            rc_path = ctx.config.rc_path
            if rc_path.exists():
                zf.write(rc_path, arcname="config/.supernannorc")
            else:
                zf.writestr("config/.supernannorc_missing.txt", "File not found.")
        except Exception as e:
            try:
                zf.writestr("config/rc_error.txt", f"Could not include .supernannorc: {e}")
            except Exception:
                pass

    def _add_system_info(self, zf: zipfile.ZipFile, diag: DiagnosticContext) -> None:
        """Adiciona informações de ambiente."""
        try:
            info: dict = {
                "app_version":    diag.app_version,
                "python_version": diag.python_ver,
                "os":             diag.os_info,
                "platform": {
                    "system":    platform.system(),
                    "release":   platform.release(),
                    "version":   platform.version(),
                    "machine":   platform.machine(),
                    "processor": platform.processor(),
                    "node":      platform.node(),
                },
                "python_info": {
                    "version":      sys.version,
                    "executable":   sys.executable,
                    "path_entries": sys.path[:5],  # Apenas os 5 primeiros para compactar
                },
                "generated_at": datetime.now().isoformat(),
            }
            zf.writestr(
                "system/environment.json",
                json.dumps(info, indent=4, ensure_ascii=False, default=str),
            )
        except Exception as e:
            try:
                zf.writestr("system/error.txt", f"Could not collect system info: {e}")
            except Exception:
                pass

    def _add_crash_info(self, zf: zipfile.ZipFile, diag: DiagnosticContext) -> None:
        """Adiciona traceback completo e estado do editor."""
        # Traceback completo
        try:
            zf.writestr("crash/traceback.txt", diag.traceback or "No traceback available.")
        except Exception:
            pass

        # Estado do editor e metadados do erro
        try:
            crash_meta: dict = {
                "exc_type":       diag.exc_type,
                "exc_time":       diag.exc_time.isoformat() if diag.exc_time else None,
                "correlation_id": diag.correlation_id,
                "fingerprint":    diag.fingerprint,
                "category":       diag.category,
                "github_labels":  diag.github_labels,
                "editor_state": {
                    "file_path":      diag.file_path,
                    "encoding":       diag.encoding,
                    "eol":            diag.eol,
                    "cursor":         diag.cursor,
                    "word_count":     diag.word_count,
                    "char_count":     diag.char_count,
                    "file_size":      diag.file_size,
                    "read_only":      diag.read_only,
                    "restore_session": diag.restore_session,
                    "backup_enabled": diag.backup_enabled,
                },
            }
            zf.writestr(
                "crash/metadata.json",
                json.dumps(crash_meta, indent=4, ensure_ascii=False, default=str),
            )
        except Exception as e:
            try:
                zf.writestr("crash/metadata_error.txt", f"Could not include crash metadata: {e}")
            except Exception:
                pass

        # Log excerpt formatado como texto legível (cópia de conveniência no bundle)
        try:
            formatter = LogExcerptFormatter()
            readable  = formatter.format_excerpt(diag.raw_recent_logs, max_entries=LOG_EXCERPT_LINES)
            zf.writestr("crash/recent_logs_readable.txt", readable)
        except Exception:
            pass


# ──────────────────────────────────────────────────────────────────────────────
# GitHubIssueFormatter
# ──────────────────────────────────────────────────────────────────────────────

class GitHubIssueFormatter:
    """
    Formata título e labels para criação de issue no GitHub.
    Separado do body para facilitar testes unitários.
    """

    def format_title(self, diag: DiagnosticContext) -> str:
        cid_part = f" [{diag.correlation_id}]" if diag.correlation_id else ""
        fp_part  = f" fp:{diag.fingerprint}"   if diag.fingerprint    else ""
        ts       = diag.exc_time.strftime("%Y-%m-%d %H:%M")
        return f"[Bug]{cid_part} {diag.exc_type} — {ts}{fp_part}"

    def format_labels(self, diag: DiagnosticContext) -> str:
        return diag.github_labels or ISSUE_LABEL


# ──────────────────────────────────────────────────────────────────────────────
# ReportProvider / GitHubReportProvider
# ──────────────────────────────────────────────────────────────────────────────

class ReportProvider:
    """Interface base para providers de report. Substituível em testes."""

    def open_url(self, url: str) -> None:
        webbrowser.open(url)


class GitHubReportProvider(ReportProvider):
    """
    Abre uma issue no GitHub com body compacto na URL.

    Garante que a URL nunca excede limites do browser construindo
    o body via IssueReportBuilder, que trunca automaticamente.
    """

    def build_url(self, title: str, body: str, labels: str = ISSUE_LABEL) -> str:
        params = {
            "title":  title,
            "body":   body,
            "labels": labels,
        }
        query = urlencode(params, quote_via=quote)
        return f"{GITHUB_ISSUES}?{query}"

    def open_report(self, title: str, body: str, labels: str = ISSUE_LABEL) -> None:
        url = self.build_url(title, body, labels=labels)
        self.open_url(url)


# ──────────────────────────────────────────────────────────────────────────────
# IssueTemplate  (mantida para compatibilidade reversa)
# ──────────────────────────────────────────────────────────────────────────────

class IssueTemplate:
    """
    Mantida para compatibilidade com código que instancia IssueTemplate diretamente.

    Internamente delega para GitHubIssueFormatter + IssueReportBuilder.
    """

    REPORT_TYPE = "Bug Report"

    def __init__(self):
        self._formatter = GitHubIssueFormatter()
        self._builder   = IssueReportBuilder()

    def render_title(self, diag: DiagnosticContext) -> str:
        return self._formatter.format_title(diag)

    def render_body(self, diag: DiagnosticContext, bundle_path: "Path | None" = None) -> str:
        return self._builder.build_body(diag, bundle_path=bundle_path)


# ──────────────────────────────────────────────────────────────────────────────
# IssueService  — único ponto de entrada público
# ──────────────────────────────────────────────────────────────────────────────

class IssueService:
    """
    Serviço de report de issues.

    Fluxo ao chamar open_report():
      1. Coleta DiagnosticContext (estado atual do app)
      2. Gera DiagnosticBundle (ZIP completo) — best-effort
      3. Monta body compacto (<= MAX_GITHUB_BODY chars) com excerpt legível
      4. Abre GitHub Issues URL no browser
      5. Notifica usuário com instrução para anexar o bundle
    """

    def __init__(
        self,
        ctx,
        provider:       "ReportProvider | None"          = None,
        template:       "IssueTemplate | None"           = None,
        bundle_service: "DiagnosticBundleService | None" = None,
        formatter:      "GitHubIssueFormatter | None"    = None,
        builder:        "IssueReportBuilder | None"      = None,
    ):
        self.ctx            = ctx
        self.provider       = provider       or GitHubReportProvider()
        self.template       = template       or IssueTemplate()
        self.bundle_service = bundle_service or DiagnosticBundleService()
        self.formatter      = formatter      or GitHubIssueFormatter()
        self.builder        = builder        or IssueReportBuilder()

        # Configurável futuramente via config
        self.telemetry_enabled = True

    # ── API pública ────────────────────────────────────────────────────

    def open_report(self) -> None:
        """
        Fluxo principal de report de issue.

        Nunca levanta exceção — todos os erros são absorvidos internamente.
        Garante que o editor nunca crasha por falha no sistema de report.
        """
        if not self.telemetry_enabled:
            self.ctx.logs.info(
                "(Issue): Reporting disabled by user preference.",
                action="ISSUE_DISABLED",
            )
            return

        if not self.ctx.last_exception:
            self.ctx.status.warning(
                "(Issue): No exception recorded. Nothing to report."
            )
            return

        try:
            self._do_open_report()
        except Exception as e:
            # Barreira final: o sistema de report NUNCA pode crashar o editor
            try:
                self.ctx.logs.error(
                    f"(Issue): Unhandled error in open_report — {e}",
                    action="ISSUE_OPEN_FATAL",
                    exc=e,
                    extra={"traceback": traceback.format_exc()},
                )
            except Exception:
                pass

            try:
                self.ctx.status.warning(
                    "(Issue): Could not open report — see logs for details."
                )
            except Exception:
                pass

    # ── Internos ──────────────────────────────────────────────────────

    def _do_open_report(self) -> None:
        """Implementação principal do fluxo de report."""

        # 1. Coleta contexto de diagnóstico
        diag = DiagnosticContext(self.ctx)

        self.ctx.logs.info(
            f"(Issue): Starting report flow for {diag.exc_type}",
            action="ISSUE_REPORT_START",
            extra={
                "correlation_id": diag.correlation_id,
                "category":       diag.category,
                "fingerprint":    diag.fingerprint,
            },
        )

        # 2. Gera bundle de diagnóstico (best-effort)
        bundle_path = self._generate_bundle(diag)

        # 3. Monta body compacto com instrução de bundle
        body   = self.builder.build_body(diag, bundle_path=bundle_path)
        title  = self.formatter.format_title(diag)
        labels = self.formatter.format_labels(diag)

        self.ctx.logs.info(
            f"(Issue): Body size={len(body)} chars (limit={MAX_GITHUB_BODY})",
            action="ISSUE_BODY_BUILT",
            extra={"body_length": len(body), "truncated": len(body) >= MAX_GITHUB_BODY},
        )

        # 4. Abre a URL no browser
        self._open_browser(title, body, labels)

        # 5. Notifica o usuário com instrução para anexar o bundle
        self._notify_user(bundle_path)

    def _generate_bundle(self, diag: DiagnosticContext) -> "Path | None":
        """Gera o bundle ZIP. Retorna o path ou None se falhar."""
        try:
            self.ctx.logs.info(
                "(Issue): Generating diagnostic bundle...",
                action="BUNDLE_START",
            )
            bundle_path = self.bundle_service.generate(diag, self.ctx)

            if bundle_path:
                self.ctx.logs.info(
                    f"(Issue): Bundle saved — {bundle_path}",
                    action="BUNDLE_SAVED",
                    extra={"bundle_path": str(bundle_path)},
                )
            else:
                self.ctx.logs.warning(
                    "(Issue): Bundle generation returned None (best-effort failure).",
                    action="BUNDLE_SKIPPED",
                )

            return bundle_path

        except Exception as e:
            # Bundle é best-effort — nunca cancela o report
            try:
                self.ctx.logs.warning(
                    f"(Issue): Bundle generation failed — {e}",
                    action="BUNDLE_FAILED",
                    extra={"traceback": traceback.format_exc()},
                )
            except Exception:
                pass
            return None

    def _open_browser(self, title: str, body: str, labels: str) -> None:
        """Abre a URL do GitHub no browser."""
        try:
            self.provider.open_report(title, body, labels=labels)
            self.ctx.logs.info(
                "(Issue): Browser opened for GitHub Issues.",
                action="ISSUE_BROWSER_OPENED",
            )
        except Exception as e:
            self.ctx.logs.error(
                f"(Issue): Failed to open browser — {e}",
                action="ISSUE_BROWSER_FAILED",
                exc=e,
            )
            self.ctx.status.warning(
                "(Issue): Could not open browser. Check logs for details."
            )
            raise  # Re-levanta para ser capturado pelo caller

    def _notify_user(self, bundle_path: "Path | None") -> None:
        """Notifica o usuário com instrução de report e path do bundle."""
        try:
            if bundle_path:
                # Notificação completa com path do bundle
                self.ctx.app.notify(
                    f"📎 Attach bundle to the GitHub issue:\n{bundle_path}",
                    title="Diagnostic Bundle Ready",
                    severity="information",
                    timeout=20,
                )
                self.ctx.status.info(
                    f"(Issue): Browser opened — attach bundle: {bundle_path.name}"
                )
            else:
                # Bundle não disponível — instrução genérica
                self.ctx.app.notify(
                    "GitHub Issues opened. Bundle unavailable — attach logs manually.",
                    title="Issue Report",
                    severity="warning",
                    timeout=12,
                )
                self.ctx.status.info(
                    "(Issue): Browser opened — review and submit the report."
                )
        except Exception:
            # Notificação é best-effort
            try:
                self.ctx.status.info("(Issue): Browser opened — review and submit.")
            except Exception:
                pass
