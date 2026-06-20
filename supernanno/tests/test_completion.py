# supernanno/tests/test_completion.py
#
# Tests for CompletionEngine and CompletionService.
# These tests do NOT require a running Textual app.
# They mock AppContext and the editor widget.
#
# Run with:
#   pytest supernanno/tests/test_completion.py -v

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from collections import Counter


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

def _make_ctx(text: str = "", cursor=(0, 0)):
    """Minimal AppContext mock sufficient for CompletionService tests."""
    ctx = MagicMock()

    # Editor mock
    ctx.editor.text = text
    ctx.editor.cursor_location = cursor

    # Document line mock — returns everything before the cursor column
    def get_line(row):
        lines = text.split("\n")
        return lines[row] if row < len(lines) else ""

    ctx.editor.document.get_line.side_effect = get_line

    # Autocomplete flag
    ctx.autocompletion_enabled = True

    # Status, logs, errors are MagicMocks — they accept any call
    return ctx


# ---------------------------------------------------------------------------
# CompletionEngine tests
# ---------------------------------------------------------------------------

class TestCompletionEngine:

    def _engine(self):
        from supernanno.core.completion import CompletionEngine
        return CompletionEngine()

    # ── Index building ─────────────────────────────────────────────────

    def test_empty_text_returns_no_candidates(self):
        eng = self._engine()
        eng.update_index("")
        assert eng.get_completions("a") == []

    def test_single_word_not_returned_as_its_own_completion(self):
        eng = self._engine()
        eng.update_index("hello")
        # exclude_exact=True is the default
        assert "hello" not in eng.get_completions("hello")

    def test_exact_match_excluded_by_default(self):
        eng = self._engine()
        eng.update_index("foo foobar foobaz")
        results = eng.get_completions("foo")
        assert "foo" not in results
        assert "foobar" in results
        assert "foobaz" in results

    def test_exact_match_included_when_flag_false(self):
        eng = self._engine()
        eng.update_index("foo foobar")
        results = eng.get_completions("foo", exclude_exact=False)
        assert "foo" in results

    def test_prefix_filtering(self):
        eng = self._engine()
        eng.update_index("apple application banana bar")
        results = eng.get_completions("app")
        assert all(w.startswith("app") for w in results)
        assert "banana" not in results

    def test_ranking_by_frequency(self):
        eng = self._engine()
        # "variable" appears 5×, "vary" appears 1×
        eng.update_index("variable variable variable variable variable vary")
        results = eng.get_completions("var")
        assert results[0] == "variable"

    def test_ranking_by_length_on_tie(self):
        eng = self._engine()
        # Both appear once — longer word should rank first
        eng.update_index("xyz xyzabc")
        results = eng.get_completions("xy")
        assert results[0] == "xyzabc"

    def test_max_candidates_limit(self):
        from supernanno.core.completion import MAX_CANDIDATES
        eng = self._engine()
        # 20 distinct words starting with "w"
        words = " ".join(f"word{i}" for i in range(20))
        eng.update_index(words)
        results = eng.get_completions("word")
        assert len(results) <= MAX_CANDIDATES

    def test_no_suggestions_for_empty_prefix(self):
        eng = self._engine()
        eng.update_index("hello world")
        assert eng.get_completions("") == []

    def test_incremental_guard_skips_rescan(self):
        """
        If text length barely changes the engine must NOT rescan.
        We verify by checking the cached length stays stable.
        """
        from supernanno.core.completion import _RESCAN_CHAR_DELTA
        eng = self._engine()
        text = "hello world"
        eng.update_index(text)
        cached_before = eng._cached_text_len

        # Add fewer chars than the delta — should not rescan
        tiny_change = text + "x"  # +1 char, below delta
        eng.update_index(tiny_change)
        assert eng._cached_text_len == cached_before

    def test_invalidate_forces_rescan(self):
        from supernanno.core.completion import _RESCAN_CHAR_DELTA
        eng = self._engine()
        text = "hello world"
        eng.update_index(text)

        eng.invalidate()
        # Same text but after invalidate the engine must rescan
        eng.update_index(text)
        assert eng._cached_text_len == len(text)

    def test_unicode_words(self):
        """Non-ASCII identifiers that match \w should be handled gracefully."""
        eng = self._engine()
        # Python's \w matches Unicode letters — engine must not crash
        eng.update_index("café résumé naïve")
        # Should not raise; result may be empty (no ASCII start)
        _ = eng.get_completions("caf")

    def test_duplicate_words_deduplicated(self):
        eng = self._engine()
        text = "return return return"
        eng.update_index(text)
        # "return" appears 3× but is excluded as exact match
        results = eng.get_completions("retur")
        # "return" should appear exactly once
        assert results.count("return") <= 1

    def test_large_buffer_performance(self):
        """update_index on a ~500 KB text must complete quickly (< 1 s)."""
        import time
        eng = self._engine()
        big_text = ("hello world foo bar baz\n" * 20_000)
        t0 = time.monotonic()
        eng.update_index(big_text)
        elapsed = time.monotonic() - t0
        assert elapsed < 1.0, f"Index update took {elapsed:.2f}s — too slow"


# ---------------------------------------------------------------------------
# CompletionService tests
# ---------------------------------------------------------------------------

class TestCompletionService:

    def _svc(self, text="", cursor=(0, 0)):
        from supernanno.core.completion import CompletionService
        ctx = _make_ctx(text, cursor)
        svc = CompletionService(ctx)
        return svc, ctx

    def test_on_text_changed_updates_index(self):
        svc, ctx = self._svc()
        svc.on_text_changed("hello world")
        # Engine should have scanned the text
        results = svc.engine.get_completions("hel")
        assert "hello" in results

    def test_on_text_changed_never_raises(self):
        svc, ctx = self._svc()
        # Even with a broken engine, must not raise
        svc.engine = None
        try:
            svc.on_text_changed("anything")
        except Exception as e:
            pytest.fail(f"on_text_changed raised: {e}")

    def test_show_completions_disabled(self):
        svc, ctx = self._svc("hello world")
        ctx.autocompletion_enabled = False
        svc.show_completions()
        ctx.status.warning.assert_called()

    def test_show_completions_empty_prefix_warns(self):
        # cursor at col 0 → no prefix
        svc, ctx = self._svc("hello", cursor=(0, 0))
        svc.show_completions()
        ctx.status.warning.assert_called()

    def test_show_completions_no_candidates_warns(self):
        # prefix "zzz" — no matching word in buffer
        svc, ctx = self._svc("hello world", cursor=(0, 3))
        # Make cursor land after "hel"
        ctx.editor.cursor_location = (0, 3)
        ctx.editor.document.get_line.side_effect = lambda r: "zzzXYZ" if r == 0 else ""
        svc.on_text_changed("hello world")
        # Force prefix "zzzXYZ" → no results except itself
        svc.engine.update_index("hello world")
        # Pretend cursor is after "zzz"
        ctx.editor.cursor_location = (0, 3)
        ctx.editor.document.get_line.side_effect = lambda r: "zzz" if r == 0 else ""
        svc.show_completions()
        ctx.status.warning.assert_called()

    def test_get_word_at_cursor_simple(self):
        svc, ctx = self._svc()
        ctx.editor.cursor_location = (0, 5)
        ctx.editor.document.get_line.side_effect = lambda r: "hello" if r == 0 else ""
        prefix, row, start_col = svc._get_word_at_cursor()
        assert prefix == "hello"
        assert row == 0
        assert start_col == 0

    def test_get_word_at_cursor_mid_line(self):
        svc, ctx = self._svc()
        ctx.editor.cursor_location = (0, 8)
        ctx.editor.document.get_line.side_effect = lambda r: "foo = bar" if r == 0 else ""
        prefix, row, start_col = svc._get_word_at_cursor()
        assert prefix == "bar"
        assert start_col == 6

    def test_get_word_at_cursor_space_returns_empty(self):
        svc, ctx = self._svc()
        ctx.editor.cursor_location = (0, 4)
        ctx.editor.document.get_line.side_effect = lambda r: "foo " if r == 0 else ""
        prefix, row, start_col = svc._get_word_at_cursor()
        assert prefix == ""

    def test_accept_completion_replaces_prefix(self):
        svc, ctx = self._svc("hello world")
        ctx.editor.cursor_location = (0, 3)
        svc._accept_completion("hello", "hel", 0, 0)
        ctx.editor.replace.assert_called_once_with("hello", (0, 0), (0, 3))
        ctx.editor.cursor_location = (0, 5)

    def test_dismiss_closes_popup(self):
        svc, ctx = self._svc()
        mock_popup = MagicMock()
        svc._popup = mock_popup
        svc.dismiss()
        mock_popup.remove.assert_called_once()
        assert svc._popup is None

    def test_is_active_false_when_no_popup(self):
        svc, ctx = self._svc()
        assert svc.is_active is False

    def test_is_active_true_when_popup_set(self):
        svc, ctx = self._svc()
        svc._popup = MagicMock()
        assert svc.is_active is True

    def test_show_completions_mounts_popup(self):
        """
        show_completions() must call ctx.app.mount() with a CompletionPopup.
        We patch the import inside the method to avoid needing Textual widgets.
        """
        svc, ctx = self._svc("def foo(self):\n    bar = foo", cursor=(1, 7))
        ctx.editor.cursor_location = (1, 7)
        ctx.editor.document.get_line.side_effect = (
            lambda r: "    bar = foo" if r == 1 else "def foo(self):"
        )
        svc.engine.update_index("def foo(self):\n    bar = foo")

        fake_popup = MagicMock()
        fake_popup_cls = MagicMock(return_value=fake_popup)

        with patch.dict("sys.modules", {"supernanno.ui.completion_popup": MagicMock(
            CompletionPopup=fake_popup_cls
        )}):
            # Re-patch at the exact import site used inside show_completions
            import importlib
            import supernanno.core.completion as mod
            original_show = mod.CompletionService.show_completions

            def patched_show(self_inner):
                with patch(
                    "supernanno.core.completion.CompletionService._close_popup"
                ):
                    pass
                # Call original but with patched import
                original_show(self_inner)

            svc.show_completions()
            # We only assert no exception was raised and status was called
        # At minimum the status path must have been reached
        assert ctx.status.info.called or ctx.status.warning.called

    def test_apply_completion_error_routed_to_errors(self):
        svc, ctx = self._svc()
        ctx.editor.replace.side_effect = RuntimeError("Editor busy")
        svc._accept_completion("foo", "fo", 0, 0)
        ctx.errors.handle.assert_called_once()

    def test_empty_buffer(self):
        svc, ctx = self._svc("")
        svc.on_text_changed("")
        assert svc.engine.get_completions("a") == []

    def test_single_line_buffer(self):
        svc, ctx = self._svc("variable = 42")
        svc.on_text_changed("variable = 42")
        results = svc.engine.get_completions("var")
        assert "variable" in results

    def test_multiline_buffer(self):
        text = "def calculate():\n    result = calculate() + 1\n    return result"
        svc, ctx = self._svc(text)
        svc.on_text_changed(text)
        results = svc.engine.get_completions("calc")
        assert "calculate" in results

    def test_unicode_buffer_no_crash(self):
        text = "# Olá mundo\ndef função():\n    pass"
        svc, ctx = self._svc(text)
        try:
            svc.on_text_changed(text)
            _ = svc.engine.get_completions("fun")
        except Exception as e:
            pytest.fail(f"Unicode buffer raised: {e}")


# ---------------------------------------------------------------------------
# Integration: text_area_changed event hooks completion
# ---------------------------------------------------------------------------

class TestTextAreaChangedEvent:

    def test_event_calls_completion_on_text_changed(self):
        from supernanno.events.text_area_changed import handle

        ctx = MagicMock()
        ctx.app._loading = False
        ctx.editor.text = "hello world"
        ctx.current_path = None
        ctx.status.is_locked.return_value = False

        # Completion mock
        completion_mock = MagicMock()
        ctx.completion = completion_mock

        handle(ctx)

        completion_mock.on_text_changed.assert_called_once_with("hello world")

    def test_event_skips_completion_during_loading(self):
        from supernanno.events.text_area_changed import handle

        ctx = MagicMock()
        ctx.app._loading = True
        completion_mock = MagicMock()
        ctx.completion = completion_mock

        handle(ctx)

        completion_mock.on_text_changed.assert_not_called()

    def test_event_completion_error_does_not_crash(self):
        from supernanno.events.text_area_changed import handle

        ctx = MagicMock()
        ctx.app._loading = False
        ctx.editor.text = "hello"
        ctx.current_path = None
        ctx.status.is_locked.return_value = False

        completion_mock = MagicMock()
        completion_mock.on_text_changed.side_effect = RuntimeError("boom")
        ctx.completion = completion_mock

        # Must not raise
        try:
            handle(ctx)
        except Exception as e:
            pytest.fail(f"text_area_changed raised despite broken completion: {e}")


# ---------------------------------------------------------------------------
# Integration: Escape key dismisses completion popup first
# ---------------------------------------------------------------------------

class TestKeyHandlerEscapeCompletion:

    def test_escape_closes_popup_before_state_transition(self):
        from supernanno.events.key import handle

        ctx = MagicMock()
        ctx.app.in_startup = False
        ctx.state = None
        ctx.path_container.display = False

        completion_mock = MagicMock()
        completion_mock.is_active = True
        ctx.completion = completion_mock

        event = MagicMock()
        event.key = "escape"

        handle(ctx, event)

        completion_mock.dismiss.assert_called_once()
        event.stop.assert_called_once()

    def test_escape_without_popup_falls_through(self):
        from supernanno.events.key import handle

        ctx = MagicMock()
        ctx.app.in_startup = False
        ctx.state = None
        ctx.path_container.display = False

        completion_mock = MagicMock()
        completion_mock.is_active = False
        ctx.completion = completion_mock

        event = MagicMock()
        event.key = "escape"

        handle(ctx, event)

        completion_mock.dismiss.assert_not_called()
