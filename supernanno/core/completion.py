# supernanno/core/completion.py
#
# CompletionEngine  — pure word-extraction + ranking (no UI, no Textual)
# CompletionService — orchestrates engine + popup lifecycle
#
# Design principles:
#   • No UI logic inside CompletionEngine (SRP)
#   • All errors caught and routed through ErrorService
#   • Popup is mounted/unmounted (never shown/hidden via display=)
#   • Incremental index: re-scan only when the document actually changed
#   • Everything fully offline — zero network / AI calls

import re
from collections import Counter
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WORD_PATTERN       = re.compile(r'\b[A-Za-z_]\w*\b')  # identifiers only
MIN_PREFIX_LEN     = 1       # minimum chars before suggesting
MAX_CANDIDATES     = 12      # popup rows shown
MAX_WORD_LEN       = 128     # skip monster strings
_RESCAN_CHAR_DELTA = 20      # re-index when text changed by this many chars


# ---------------------------------------------------------------------------
# CompletionEngine — pure logic, zero Textual imports
# ---------------------------------------------------------------------------

class CompletionEngine:
    """
    Extracts candidate words from a text buffer, caches the word-frequency
    index, and provides filtered + ranked suggestions for a given prefix.

    Thread-safety: single-threaded (always called from Textual event loop).
    """

    def __init__(self) -> None:
        self._cached_text_len: int = -1
        self._word_freq: Counter   = Counter()

    # ── Public API ────────────────────────────────────────────────────

    def update_index(self, text: str) -> None:
        """
        Rebuild the word-frequency index.

        Incremental guard: only rescans when the text length changed by at
        least _RESCAN_CHAR_DELTA characters *since the last scan*, preventing
        per-keystroke full rescans on large files.

        The very first call (self._cached_text_len == -1) always scans.
        """
        current_len = len(text)
        # First call always scans; subsequent calls only if delta exceeded
        if self._cached_text_len != -1 and abs(current_len - self._cached_text_len) < _RESCAN_CHAR_DELTA:
            return

        words = WORD_PATTERN.findall(text)
        self._word_freq = Counter(
            w for w in words if len(w) <= MAX_WORD_LEN
        )
        self._cached_text_len = current_len

    def get_completions(self, prefix: str, exclude_exact: bool = True) -> list:
        """
        Return up to MAX_CANDIDATES candidates for *prefix*, ranked by:
          1. Frequency (descending) — more-used words first
          2. Length (descending)    — longer completions first (tie-break)
          3. Lexicographic (asc)    — deterministic tie-break

        If exclude_exact is True the prefix itself is not returned.
        """
        if not prefix or len(prefix) < MIN_PREFIX_LEN:
            return []

        candidates = [
            (freq, word)
            for word, freq in self._word_freq.items()
            if word.startswith(prefix) and (not exclude_exact or word != prefix)
        ]

        # Sort: highest frequency first, then longest word, then alpha
        candidates.sort(key=lambda t: (-t[0], -len(t[1]), t[1]))
        return [word for _, word in candidates[:MAX_CANDIDATES]]

    def invalidate(self) -> None:
        """Force a full rescan on the next update_index() call."""
        self._cached_text_len = -1
        self._word_freq       = Counter()


# ---------------------------------------------------------------------------
# CompletionService — orchestrates engine, popup, and ctx integration
# ---------------------------------------------------------------------------

class CompletionService:
    """
    Coordinates between:
      - CompletionEngine  (suggestion logic)
      - CompletionPopup   (UI widget, lazy-imported to avoid circular deps)
      - AppContext         (editor, status, errors, logs)

    Responsibilities:
      - Triggered on demand (Ctrl+G) or via on_text_changed hook
      - Extracts the current word prefix from the editor
      - Updates the engine index incrementally
      - Mounts / unmounts the popup widget
      - Applies the accepted completion back to the editor
      - Routes all exceptions through ErrorService
    """

    def __init__(self, ctx) -> None:
        self.ctx    = ctx
        self.engine = CompletionEngine()
        self._popup: Optional[object] = None

    # ── Public entry points ───────────────────────────────────────────

    def on_text_changed(self, text: str) -> None:
        """
        Called by events/text_area_changed.py on every TextArea.Changed.
        Updates the index incrementally — does NOT show the popup.
        The popup is only shown on explicit Ctrl+G.
        """
        try:
            self.engine.update_index(text)
        except Exception as e:
            self.ctx.errors.handle(e, action="COMPLETION_INDEX_UPDATE")

    def show_completions(self) -> None:
        """
        Invoked by action_complete_word() (Ctrl+G).
        Extracts prefix at cursor, queries the engine, mounts the popup.
        """
        if not getattr(self.ctx, "autocompletion_enabled", True):
            self.ctx.status.warning("(SuperSense): Autocomplete disabled")
            return

        try:
            prefix, row, start_col = self._get_word_at_cursor()
        except Exception as e:
            self.ctx.errors.handle(e, action="COMPLETION_GET_CURSOR_WORD")
            return

        if not prefix:
            self.ctx.status.warning(
                "(SuperSense): Type at least one character to complete"
            )
            return

        # Always update the index before querying (cheap guard inside engine)
        try:
            self.engine.update_index(self.ctx.editor.text)
        except Exception as e:
            self.ctx.errors.handle(e, action="COMPLETION_INDEX_UPDATE_PRE_SHOW")
            return

        try:
            candidates = self.engine.get_completions(prefix)
        except Exception as e:
            self.ctx.errors.handle(e, action="COMPLETION_GET_CANDIDATES")
            return

        if not candidates:
            self.ctx.status.warning(
                f"(SuperSense): No suggestions for '{prefix}'"
            )
            return

        self._close_popup()

        def on_select(word: str) -> None:
            self._accept_completion(word, prefix, row, start_col)

        try:
            # Lazy import avoids circular-import chain at module load time
            from ..ui.completion_popup import CompletionPopup

            self._popup = CompletionPopup(
                candidates,
                on_select_callback=on_select,
                on_close_callback=self._on_popup_closed,
            )
            self.ctx.app.mount(self._popup)
        except Exception as e:
            self._popup = None
            self.ctx.errors.handle(e, action="COMPLETION_POPUP_MOUNT")
            return

        self.ctx.logs.info(
            f"(SuperSense): Showing {len(candidates)} suggestions for '{prefix}'",
            action="COMPLETION_SHOW",
        )
        self.ctx.status.info(
            f"(SuperSense): {len(candidates)} suggestions — "
            "↑/↓ navigate · Tab/Enter accept · Esc close"
        )

    def dismiss(self) -> None:
        """Programmatically close the popup (e.g. on Escape in key.py)."""
        self._close_popup()

    @property
    def is_active(self) -> bool:
        """True while the completion popup is mounted and visible."""
        return self._popup is not None

    # ── Private helpers ───────────────────────────────────────────────

    def _get_word_at_cursor(self) -> tuple:
        """
        Returns (prefix, row, start_col).

        Uses a right-anchored regex on the text before the cursor to find
        the longest valid identifier fragment on that line.
        """
        editor = self.ctx.editor
        if not editor:
            return "", 0, 0

        row, col = editor.cursor_location
        line = ""
        try:
            line = editor.document.get_line(row) or ""
        except Exception:
            pass

        text_before = line[:col]
        match       = re.search(r'([A-Za-z_]\w*)$', text_before)
        prefix      = match.group(1) if match else ""
        start_col   = col - len(prefix)
        return prefix, row, start_col

    def _accept_completion(
        self, word: str, prefix: str, row: int, start_col: int
    ) -> None:
        """Replace the current prefix with *word* in the editor."""
        editor = self.ctx.editor
        try:
            start = (row, start_col)
            end   = (row, start_col + len(prefix))
            editor.replace(word, start, end)
            editor.cursor_location = (row, start_col + len(word))
            editor.focus()
            self.ctx.logs.info(
                f"(SuperSense): Accepted '{word}' (replaced '{prefix}')",
                action="COMPLETION_ACCEPT",
            )
            self.ctx.status.success(f"(SuperSense): ✓ {word}")
        except Exception as e:
            self.ctx.errors.handle(e, action="COMPLETION_APPLY")
        finally:
            self._popup = None

    def _close_popup(self) -> None:
        if self._popup is not None:
            try:
                self._popup.remove()
            except Exception:
                pass
            self._popup = None

    def _on_popup_closed(self) -> None:
        """Callback invoked by CompletionPopup when it removes itself."""
        self._popup = None
        try:
            self.ctx.editor.focus()
        except Exception:
            pass
