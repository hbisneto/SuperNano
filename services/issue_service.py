# services/issue_service.py

import platform
import sys
import traceback
import webbrowser
from datetime import datetime
from urllib.parse import urlencode, quote
from core.__version__ import VERSION

GITHUB_REPO   = "hbisneto/SuperNanno"
GITHUB_ISSUES = f"https://github.com/{GITHUB_REPO}/issues/new"
ISSUE_LABEL   = "bug"


class ReportProvider:
    def open_url(self, url: str) -> None:
        webbrowser.open(url)


class GitHubReportProvider(ReportProvider):
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


class DiagnosticContext:
    """
    Coleta o contexto completo do editor e do ambiente no momento do erro,
    para popular o template do issue no GitHub.
    """

    def __init__(self, ctx):
        self.traceback       = ctx.last_exception        or "No traceback available."
        self.exc_type        = ctx.last_exception_type   or "Unknown"
        self.exc_time        = ctx.last_exception_time   or datetime.now()
        self.correlation_id  = getattr(ctx, "last_correlation_id", "")
        self.category        = getattr(ctx, "last_error_category",  "UNCLASSIFIED_ERROR")
        self.github_labels   = getattr(ctx, "last_error_labels",    ISSUE_LABEL)
        self.fingerprint     = getattr(ctx, "last_fingerprint",     "")
        self.recent_logs     = self._get_logs(ctx)
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
    def _get_logs(ctx) -> str:
        try:
            return ctx.logs.get_recent_logs(lines=30)
        except Exception as e:
            # Log da falha em coletar logs (irônico, mas importante)
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
        return (
            f"{platform.system()} {platform.release()} "
            f"({platform.machine()})"
        )

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


class IssueTemplate:
    REPORT_TYPE = "Bug Report"

    def render_title(self, diag: DiagnosticContext) -> str:
        cid   = f" [{diag.correlation_id}]" if diag.correlation_id else ""
        fp    = f" fp:{diag.fingerprint}"   if diag.fingerprint    else ""
        ts    = diag.exc_time.strftime("%Y-%m-%d %H:%M")
        return f"[{self.REPORT_TYPE}]{cid} {diag.exc_type} — {ts}{fp}"

    def render_body(self, diag: DiagnosticContext) -> str:
        cid_section = (
            f"\n**Correlation ID:** `{diag.correlation_id}`  \n"
            f"**Fingerprint:** `{diag.fingerprint}`  \n"
            f"**Category:** `{diag.category}`"
        ) if diag.correlation_id else ""

        return f"""\
## Bug Report — SuperNanno {diag.app_version}

> This report was generated automatically. Please review and add any \
additional context before submitting.
{cid_section}

---

### Environment

| Field      | Value                                          |
|------------|------------------------------------------------|
| OS         | {diag.os_info}                                 |
| Python     | {diag.python_ver}                              |
| SuperNanno | {diag.app_version}                             |
| Time       | {diag.exc_time.strftime('%Y-%m-%d %H:%M:%S')} |

---

### Editor State

| Field          | Value                   |
|----------------|-------------------------|
| File           | {diag.file_path}        |
| Encoding       | {diag.encoding}         |
| EOL            | {diag.eol}              |
| Cursor         | {diag.cursor}           |
| Words          | {diag.word_count}       |
| Characters     | {diag.char_count}       |
| File Size      | {diag.file_size}        |
| Read-Only      | {diag.read_only}        |
| Backup Enabled | {diag.backup_enabled}   |

---

### Exception

**Type:** `{diag.exc_type}`  
**Category:** `{diag.category}`

```
{diag.traceback}
```

---

### Recent Logs (last 30 lines)

```
{diag.recent_logs}
```

---

### Steps to Reproduce

<!-- Please describe what you were doing when this error occurred -->

1.
2.
3.

### Expected Behavior

<!-- What did you expect to happen? -->

### Actual Behavior

<!-- What actually happened? -->
"""


# ─────────────────────────────────────────────────────────────────────
# IssueService — API pública usada pelo restante do app
# ─────────────────────────────────────────────────────────────────────

class IssueService:
    def __init__(
        self,
        ctx,
        provider: "ReportProvider | None" = None,
        template: "IssueTemplate | None"  = None,
    ):
        self.ctx               = ctx
        self.provider          = provider or GitHubReportProvider()
        self.template          = template or IssueTemplate()
        self.telemetry_enabled = True  # TODO (future): read from config

    def open_report(self) -> None:
        if not self.telemetry_enabled:
            self.ctx.logs.info("(Issue): Reporting disabled by user preference.")
            return

        if not self.ctx.last_exception:
            self.ctx.status.warning(
                "(Issue): No exception recorded. Nothing to report."
            )
            return

        try:
            diag   = DiagnosticContext(self.ctx)
            title  = self.template.render_title(diag)
            body   = self.template.render_body(diag)
            labels = diag.github_labels

            self.ctx.logs.info(
                f"(Issue): Opening GitHub report for {diag.exc_type}",
                action="ISSUE_OPEN",
                extra={
                    "correlation_id": diag.correlation_id,
                    "category":       diag.category,
                    "fingerprint":    diag.fingerprint,
                },
            )

            self.provider.open_report(title, body, labels=labels)

            self.ctx.status.info(
                "(Issue): Browser opened — review and submit the report."
            )

        except Exception as e:
            # O sistema de report nunca pode crashar o editor.
            tb = traceback.format_exc()
            self.ctx.logs.error(
                f"(Issue): Failed to open report — {e}",
                action="ISSUE_OPEN_FAILED",
                exc=e,
                extra={"traceback": tb},
            )
            self.ctx.status.warning("(Issue): Could not open browser.")
