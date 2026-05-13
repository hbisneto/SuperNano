# services/issue_service.py

import platform
import sys
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
            "title": title,
            "body":  body,
            "labels": labels,
        }
        query = urlencode(params, quote_via=quote)
        return f"{GITHUB_ISSUES}?{query}"

    def open_report(self, title: str, body: str) -> None:
        url = self.build_url(title, body)
        self.open_url(url)

class DiagnosticContext:
    def __init__(self, ctx):
        self.traceback   = ctx.last_exception or "No traceback available."
        self.exc_type    = ctx.last_exception_type or "Unknown"
        self.exc_time    = ctx.last_exception_time or datetime.now()
        self.recent_logs = self._get_logs(ctx)
        self.os_info     = self._get_os()
        self.python_ver  = sys.version.split()[0]
        self.app_version = VERSION
        self.file_path   = str(ctx.current_path) if ctx.current_path else "No file open"
        self.encoding    = getattr(ctx, "encoding", "UTF-8")
        self.cursor      = self._get_cursor(ctx)
        self.word_count  = getattr(ctx, "word_count", 0)
        self.char_count  = getattr(ctx, "char_count", 0)
        self.file_size   = ctx.format_size(getattr(ctx, "file_size", 0))
        self.eol         = getattr(ctx, "eol", "LF")

    @staticmethod
    def _get_logs(ctx) -> str:
        try:
            return ctx.logs.get_recent_logs(lines=30)
        except Exception:
            return "Could not retrieve logs."

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
        except Exception:
            return "N/A"

class IssueTemplate:
    REPORT_TYPE = "Bug Report"

    def render_title(self, diag: DiagnosticContext) -> str:
        return f"[{self.REPORT_TYPE}] {diag.exc_type} — {diag.exc_time.strftime('%Y-%m-%d %H:%M')}"

    def render_body(self, diag: DiagnosticContext) -> str:
        return f"""
## Bug Report — SuperNanno {diag.app_version}

> This report was generated automatically. Please review and add any \
additional context before submitting.

---

### Environment

| Field          | Value                          |
|----------------|-------------------------------|
| OS             | {diag.os_info}                |
| Python         | {diag.python_ver}             |
| SuperNanno     | {diag.app_version}            |
| Time           | {diag.exc_time.strftime('%Y-%m-%d %H:%M:%S')} |

---

### Editor State

| Field          | Value                          |
|----------------|-------------------------------|
| File           | {diag.file_path}              |
| Encoding       | {diag.encoding}               |
| EOL            | {diag.eol}                    |
| Cursor         | {diag.cursor}                 |
| Words          | {diag.word_count}             |
| Characters     | {diag.char_count}             |
| File Size      | {diag.file_size}              |

---

### Exception

**Type:** `{diag.exc_type}`
{diag.traceback}
---

### Recent Logs (last 30 lines)
{diag.recent_logs}


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


# ─────────────────────────────────────────────────────────────
# IssueService — the public API used by the rest of the app
# ─────────────────────────────────────────────────────────────

class IssueService:
    def __init__(
        self,
        ctx,
        provider: ReportProvider | None = None,
        template: IssueTemplate | None = None,
    ):
        self.ctx              = ctx
        self.provider         = provider or GitHubReportProvider()
        self.template         = template or IssueTemplate()
        self.telemetry_enabled = True   # TODO (future): read from config

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
            diag  = DiagnosticContext(self.ctx)
            title = self.template.render_title(diag)
            body  = self.template.render_body(diag)

            self.ctx.logs.info(
                f"(Issue): Opening GitHub report for {diag.exc_type}"
            )

            self.provider.open_report(title, body)

            self.ctx.status.info(
                "(Issue): Browser opened — review and submit the report."
            )

        except Exception as e:
            # Never let the reporting system itself crash the editor.
            self.ctx.logs.error(f"(Issue): Failed to open report — {e}")
            self.ctx.status.warning("(Issue): Could not open browser.")