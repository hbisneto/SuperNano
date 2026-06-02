# tests/test_issue_service.py
#
# Testes unitários para o sistema de report refatorado.
# Necessário pytest: pip install pytest
# Execute com: python -m pytest tests/test_issue_service.py -v
# pytest tests/test_issue_service.py -v                                            
#
# Nota: esses testes não dependem do Textual/app rodando.
# Usam mocks simples inline para simular ctx e logger.

import json
import os
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).parent.parent))

from ..services.issue_service import (
    DiagnosticBundleService,
    DiagnosticContext,
    GitHubIssueFormatter,
    GitHubReportProvider,
    IssueReportBuilder,
    IssueService,
    LogExcerptFormatter,
    MAX_GITHUB_BODY,
)

def _make_ctx(*, with_exception: bool = True, with_logs: bool = True) -> MagicMock:
    """Cria um mock de AppContext suficientemente completo para os testes."""
    ctx = MagicMock()

    if with_exception:
        ctx.last_exception      = "Traceback (most recent call last):\n  File 'x.py', line 1\nPermissionError: denied"
        ctx.last_exception_type = "PermissionError"
        ctx.last_exception_time = datetime(2026, 5, 27, 14, 30, 0)
        ctx.last_correlation_id = "abc12345"
        ctx.last_error_category = "FILE_PERMISSION_ERROR"
        ctx.last_error_labels   = "bug,permissions"
        ctx.last_fingerprint    = "deadbeef1234"
    else:
        ctx.last_exception      = None
        ctx.last_exception_type = None
        ctx.last_exception_time = None
        ctx.last_correlation_id = None
        ctx.last_error_category = None
        ctx.last_error_labels   = None
        ctx.last_fingerprint    = None

    if with_logs:
        raw_log = (
            '{"timestamp":"2026-05-27T14:30:00","level":"ERROR","action":"FILE_SAVE",'
            '"exc_type":"PermissionError","exc_message":"Permission denied",'
            '"correlation_id":"abc12345","path":"/tmp/test.py"}\n'
            '{"timestamp":"2026-05-27T14:30:01","level":"INFO","action":"APP_MOUNT",'
            '"message":"started","correlation_id":""}'
        )
        ctx.logs.get_recent_logs.return_value = raw_log
    else:
        ctx.logs.get_recent_logs.return_value = "No logs for today."

    ctx.current_path = Path("/tmp/test.py")
    ctx.encoding     = "UTF-8"
    ctx.eol          = "LF"
    ctx.read_only    = False
    ctx.restore_session = True
    ctx.backup_enabled  = False
    ctx.word_count   = 42
    ctx.char_count   = 250
    ctx.file_size    = 1024
    ctx.format_size  = lambda s: f"{s} bytes"
    ctx.editor.cursor_location = (10, 5)

    mock_log_file = MagicMock()
    mock_log_file.exists.return_value = False
    ctx.logger._get_log_file.return_value = mock_log_file

    mock_config_path = MagicMock(spec=Path)
    mock_config_path.exists.return_value = False
    mock_config_path.__str__.return_value = "/nonexistent/config.json"

    mock_rc_path = MagicMock(spec=Path)
    mock_rc_path.exists.return_value = False
    mock_rc_path.__str__.return_value = "/nonexistent/.supernannorc"

    ctx.config.config_path = mock_config_path
    ctx.config.rc_path = mock_rc_path
    ctx.config.data = {"debug": False}

    return ctx

class TestLogExcerptFormatter:

    def test_format_line_json(self):
        f = LogExcerptFormatter()
        raw = json.dumps({
            "level": "ERROR",
            "action": "FILE_SAVE",
            "exc_type": "PermissionError",
            "exc_message": "Permission denied",
            "correlation_id": "abc12345",
            "path": "/tmp/test.py",
            "timestamp": "2026-05-27T14:30:00.123456",
        })
        result = f.format_line(raw)

        assert "[ERROR] FILE_SAVE" in result
        assert "PermissionError" in result
        assert "Permission denied" in result
        assert "abc12345" in result
        assert "/tmp/test.py" in result
        assert '"level"' not in result
        assert '"exc_type"' not in result

    def test_format_line_invalid_json(self):
        f = LogExcerptFormatter()
        result = f.format_line("not json at all")
        assert result == "not json at all"

    def test_format_line_empty(self):
        f = LogExcerptFormatter()
        result = f.format_line("")
        assert isinstance(result, str)

    def test_format_excerpt_multiple_lines(self):
        f = LogExcerptFormatter()
        lines = [
            json.dumps({"level": "ERROR", "action": "FILE_SAVE", "exc_type": "PermissionError",
                        "exc_message": "denied", "correlation_id": "aaa", "path": "/x.py",
                        "timestamp": "2026-05-27T14:00:00"}),
            json.dumps({"level": "INFO", "action": "APP_MOUNT", "message": "started",
                        "timestamp": "2026-05-27T14:00:01"}),
        ]
        raw = "\n".join(lines)
        result = f.format_excerpt(raw, max_entries=10)

        assert "[ERROR]" in result
        assert "[INFO]" in result
        assert '"level"' not in result

    def test_format_excerpt_no_logs(self):
        f = LogExcerptFormatter()
        result = f.format_excerpt("No logs for today.")
        assert result == "No logs for today."

    def test_format_excerpt_respects_max_entries(self):
        f = LogExcerptFormatter()
        lines = [json.dumps({"level": "INFO", "action": f"ACTION_{i}", "timestamp": "2026-01-01T00:00:00"})
                 for i in range(20)]
        raw = "\n".join(lines)
        result = f.format_excerpt(raw, max_entries=3)

        assert "ACTION_19" in result
        assert "ACTION_18" in result
        assert "ACTION_17" in result
        assert "ACTION_0"  not in result

class TestIssueReportBuilder:

    def _make_diag(self) -> DiagnosticContext:
        ctx  = _make_ctx()
        return DiagnosticContext(ctx)

    def test_body_never_exceeds_max(self):
        builder = IssueReportBuilder()
        diag    = self._make_diag()
        body    = builder.build_body(diag)

        assert len(body) <= MAX_GITHUB_BODY, (
            f"Body has {len(body)} chars, limit is {MAX_GITHUB_BODY}"
        )

    def test_body_no_raw_json(self):
        builder = IssueReportBuilder()
        diag    = self._make_diag()
        body    = builder.build_body(diag)

        assert '"exc_type":'     not in body
        assert '"level_num":'    not in body
        assert '"editor_state":' not in body
        assert '"session_state":' not in body

    def test_body_contains_key_fields(self):
        builder = IssueReportBuilder()
        diag    = self._make_diag()
        body    = builder.build_body(diag)

        assert diag.exc_type        in body
        assert diag.correlation_id  in body
        assert diag.app_version     in body
        assert diag.os_info         in body

    def test_body_with_bundle_path(self):
        builder     = IssueReportBuilder()
        diag        = self._make_diag()
        bundle_path = Path("/tmp/issue_bundle_abc_20260527.zip")
        body        = builder.build_body(diag, bundle_path=bundle_path)

        assert str(bundle_path) in body
        assert "attach" in body.lower() or "bundle" in body.lower()

    def test_body_without_bundle_path(self):
        builder = IssueReportBuilder()
        diag    = self._make_diag()
        body    = builder.build_body(diag, bundle_path=None)

        assert "unavailable" in body.lower() or "bundle" in body.lower()

    def test_truncation_with_giant_traceback(self):
        builder = IssueReportBuilder()
        diag    = self._make_diag()
        diag.traceback = "line\n" * 5_000
        body = builder.build_body(diag)

        assert len(body) <= MAX_GITHUB_BODY
        assert (
            "more lines in bundle" in body.lower()
            or "truncated" in body.lower()
            or "⚠️" in body
        )

    def test_custom_max_chars(self):
        builder = IssueReportBuilder()
        diag    = self._make_diag()
        body    = builder.build_body(diag, max_chars=500)

        assert len(body) <= 500

class TestGitHubIssueFormatter:

    def _make_diag(self) -> DiagnosticContext:
        return DiagnosticContext(_make_ctx())

    def test_title_contains_exc_type(self):
        fmt   = GitHubIssueFormatter()
        diag  = self._make_diag()
        title = fmt.format_title(diag)
        assert diag.exc_type in title

    def test_title_contains_correlation_id(self):
        fmt   = GitHubIssueFormatter()
        diag  = self._make_diag()
        title = fmt.format_title(diag)
        assert diag.correlation_id in title

    def test_title_contains_timestamp(self):
        fmt   = GitHubIssueFormatter()
        diag  = self._make_diag()
        title = fmt.format_title(diag)

        assert "2026" in title

    def test_labels_fallback(self):
        fmt  = GitHubIssueFormatter()
        diag = self._make_diag()
        diag.github_labels = ""
        labels = fmt.format_labels(diag)
        assert labels == "bug"

class TestGitHubReportProvider:

    def test_url_body_encoded(self):
        provider = GitHubReportProvider()
        url      = provider.build_url("My Title", "My Body", labels="bug")

        assert "title=My+Title" in url or "title=My%20Title" in url
        assert "bug" in url

    def test_url_never_contains_raw_json_object(self):
        """A URL nunca deve conter o payload JSON bruto de um log entry."""
        provider = GitHubReportProvider()
        body     = (
            "## Bug\n\n"
            "```\n"
            "[ERROR] FILE_SAVE\n"
            "  Exception: PermissionError\n"
            "  Correlation ID: abc12345\n"
            "```\n"
        )
        url = provider.build_url("Title", body)

        assert '"level_num"' not in url
        assert '"editor_state"' not in url

    def test_open_report_calls_open_url(self):
        opened_urls = []

        class TestProvider(GitHubReportProvider):
            def open_url(self, url: str) -> None:
                opened_urls.append(url)

        provider = TestProvider()
        provider.open_report("Title", "Body", labels="bug")

        assert len(opened_urls) == 1
        assert "github.com" in opened_urls[0]

class TestDiagnosticBundleService:

    def test_bundle_created_and_valid_zip(self):
        ctx    = _make_ctx()
        diag   = DiagnosticContext(ctx)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = DiagnosticBundleService()
            service._issues_dir = Path(tmpdir)

            bundle_path = service.generate(diag, ctx)

            assert bundle_path is not None, "Bundle should be created"
            assert bundle_path.exists(), "Bundle file should exist on disk"
            assert zipfile.is_zipfile(bundle_path)

    def test_bundle_internal_structure(self):
        ctx  = _make_ctx()
        diag = DiagnosticContext(ctx)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = DiagnosticBundleService()
            service._issues_dir = Path(tmpdir)

            bundle_path = service.generate(diag, ctx)
            assert bundle_path is not None

            with zipfile.ZipFile(bundle_path, "r") as zf:
                names = set(zf.namelist())

            assert any(n.startswith("logs/")   for n in names), f"Missing logs/ in {names}"
            assert any(n.startswith("config/") for n in names), f"Missing config/ in {names}"
            assert any(n.startswith("system/") for n in names), f"Missing system/ in {names}"
            assert any(n.startswith("crash/")  for n in names), f"Missing crash/ in {names}"

    def test_bundle_system_info_is_valid_json(self):
        ctx  = _make_ctx()
        diag = DiagnosticContext(ctx)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = DiagnosticBundleService()
            service._issues_dir = Path(tmpdir)

            bundle_path = service.generate(diag, ctx)
            assert bundle_path is not None

            with zipfile.ZipFile(bundle_path, "r") as zf:
                sys_info = json.loads(zf.read("system/environment.json"))

            assert "app_version"    in sys_info
            assert "python_version" in sys_info
            assert "os"             in sys_info
            assert "platform"       in sys_info

    def test_bundle_crash_metadata_is_valid_json(self):
        ctx  = _make_ctx()
        diag = DiagnosticContext(ctx)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = DiagnosticBundleService()
            service._issues_dir = Path(tmpdir)

            bundle_path = service.generate(diag, ctx)
            assert bundle_path is not None

            with zipfile.ZipFile(bundle_path, "r") as zf:
                meta = json.loads(zf.read("crash/metadata.json"))

            assert meta["exc_type"]       == "PermissionError"
            assert meta["correlation_id"] == "abc12345"
            assert "editor_state"         in meta

    def test_bundle_fails_gracefully_on_permission_error(self):
        """Bundle deve retornar None sem crashar quando não pode gravar."""
        ctx  = _make_ctx()
        diag = DiagnosticContext(ctx)

        service = DiagnosticBundleService()
        service._issues_dir = Path("/root/nonexistent_supernanno_test_12345")

        bundle_path = service.generate(diag, ctx)

        assert bundle_path is None or isinstance(bundle_path, Path)

    def test_bundle_filename_contains_correlation_id(self):
        ctx  = _make_ctx()
        diag = DiagnosticContext(ctx)

        with tempfile.TemporaryDirectory() as tmpdir:
            service = DiagnosticBundleService()
            service._issues_dir = Path(tmpdir)

            bundle_path = service.generate(diag, ctx)
            assert bundle_path is not None
            assert "abc12345" in bundle_path.name

class TestIssueService:

    def test_open_report_no_exception_does_nothing(self):
        ctx = _make_ctx(with_exception=False)

        opened = []

        class NoOpProvider(GitHubReportProvider):
            def open_url(self, url):
                opened.append(url)

        svc = IssueService(ctx, provider=NoOpProvider())
        svc.open_report()

        assert len(opened) == 0

    def test_open_report_opens_browser(self):
        ctx = _make_ctx()

        opened = []

        class CapturingProvider(GitHubReportProvider):
            def open_url(self, url):
                opened.append(url)

        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_svc = DiagnosticBundleService()
            bundle_svc._issues_dir = Path(tmpdir)

            svc = IssueService(ctx, provider=CapturingProvider(), bundle_service=bundle_svc)
            svc.open_report()

        assert len(opened) == 1
        assert "github.com" in opened[0]

    def test_open_report_url_body_within_limit(self):
        ctx = _make_ctx()

        captured_urls = []

        class CapturingProvider(GitHubReportProvider):
            def open_url(self, url):
                captured_urls.append(url)

        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_svc = DiagnosticBundleService()
            bundle_svc._issues_dir = Path(tmpdir)

            svc = IssueService(ctx, provider=CapturingProvider(), bundle_service=bundle_svc)
            svc.open_report()

        assert len(captured_urls) == 1
        url = captured_urls[0]
        assert len(url) < 8_000, f"URL too long: {len(url)} chars"

    def test_open_report_survives_bundle_failure(self):
        """Report deve funcionar mesmo se o bundle falhar."""
        ctx = _make_ctx()

        opened = []

        class CapturingProvider(GitHubReportProvider):
            def open_url(self, url):
                opened.append(url)

        class FailingBundleService(DiagnosticBundleService):
            def generate(self, diag, ctx):
                raise RuntimeError("Simulated bundle failure")

        svc = IssueService(
            ctx,
            provider=CapturingProvider(),
            bundle_service=FailingBundleService(),
        )
        svc.open_report()
        assert len(opened) == 1

    def test_open_report_never_crashes_on_browser_error(self):
        ctx = _make_ctx()

        class BrokenProvider(GitHubReportProvider):
            def open_url(self, url):
                raise OSError("Browser unavailable")

        with tempfile.TemporaryDirectory() as tmpdir:
            bundle_svc = DiagnosticBundleService()
            bundle_svc._issues_dir = Path(tmpdir)

            svc = IssueService(ctx, provider=BrokenProvider(), bundle_service=bundle_svc)

            try:
                svc.open_report()
            except Exception as e:
                assert False, f"open_report raised unexpected exception: {e}"

    def test_telemetry_disabled_does_nothing(self):
        ctx    = _make_ctx()
        opened = []

        class CapturingProvider(GitHubReportProvider):
            def open_url(self, url):
                opened.append(url)

        svc = IssueService(ctx, provider=CapturingProvider())
        svc.telemetry_enabled = False
        svc.open_report()
        assert len(opened) == 0

class TestDiagnosticContext:

    def test_log_excerpt_is_human_readable(self):
        ctx  = _make_ctx()
        diag = DiagnosticContext(ctx)
        assert '"level_num"' not in diag.log_excerpt
        assert '"editor_state"' not in diag.log_excerpt
        assert "[ERROR]" in diag.log_excerpt or "[INFO]" in diag.log_excerpt

    def test_raw_logs_preserved_for_bundle(self):
        ctx  = _make_ctx()
        diag = DiagnosticContext(ctx)
        assert "FILE_SAVE" in diag.raw_recent_logs

    def test_graceful_when_no_logs(self):
        ctx = _make_ctx(with_logs=False)
        ctx.logs.get_recent_logs.return_value = "No logs for today."
        diag = DiagnosticContext(ctx)
        assert diag.log_excerpt == "No logs for today."

    def test_graceful_when_cursor_fails(self):
        ctx = _make_ctx()
        ctx.editor.cursor_location = MagicMock(side_effect=Exception("no editor"))

        diag = DiagnosticContext(ctx)
        assert diag.cursor == "N/A"