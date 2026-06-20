# supernanno/ui/completion_popup.py
#
# CompletionPopup — Textual widget that renders the autocomplete suggestion
# list as a floating panel anchored near the cursor.
#
# Architecture notes:
#   • This widget owns NO business logic (word extraction, ranking, etc.)
#   • It receives a ready-made list[str] from CompletionService
#   • It communicates back via two callbacks:
#       on_select_callback(word: str)  — user accepted a suggestion
#       on_close_callback()            — popup is closing (for cleanup)
#   • Self-removes on Escape, Tab-accept, Enter-accept
#   • Never crashes the editor: all exceptions are silently swallowed
#     (a broken popup must not take down the editor)
#
# TCSS rules live in style.tcss (see #completion_popup, .completion_item).

from __future__ import annotations

from typing import Callable, List

from textual.app import ComposeResult
from textual.containers import Vertical
from textual import events
from textual.widgets import ListView, ListItem, Label


class CompletionPopup(Vertical):
    """
    A floating autocomplete suggestion list.

    Lifecycle
    ---------
    Mounted by CompletionService.show_completions().
    Unmounts itself when the user accepts, dismisses, or presses Escape.

    Keyboard contracts
    ------------------
    ↑ / ↓      → navigate the list (handled by ListView natively)
    Tab        → accept highlighted suggestion
    Enter      → accept highlighted suggestion
    Escape     → close without accepting
    Any other  → propagate to editor (stop_propagation stays False)
    """

    DEFAULT_CSS = ""  # All CSS lives in style.tcss

    def __init__(
        self,
        candidates: List[str],
        on_select_callback: Callable[[str], None],
        on_close_callback: Callable[[], None],
    ) -> None:
        super().__init__(id="completion_popup")
        self._candidates          = candidates
        self._on_select_callback  = on_select_callback
        self._on_close_callback   = on_close_callback

    # ── Compose ───────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        with ListView(id="completion_list"):
            for word in self._candidates:
                yield ListItem(Label(word), classes="completion_item")

    # ── Lifecycle ─────────────────────────────────────────────────────

    def on_mount(self) -> None:
        """Focus the list immediately so arrow keys work."""
        try:
            self.query_one(ListView).focus()
        except Exception:
            pass

    # ── Key handling ──────────────────────────────────────────────────

    def on_key(self, event: events.Key) -> None:
        key = event.key

        if key in ("tab", "enter"):
            self._accept_highlighted()
            event.stop()
            return

        if key == "escape":
            self._close()
            event.stop()
            return

        # ↑ and ↓ are handled natively by ListView — do NOT stop them.
        # Any other character should propagate back to the editor.

    # ── ListView selection (mouse click) ──────────────────────────────

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Mouse-click selection."""
        try:
            word = event.item.query_one(Label).renderable
            self._accept(str(word))
        except Exception:
            self._close()
        event.stop()

    # ── Private helpers ───────────────────────────────────────────────

    def _accept_highlighted(self) -> None:
        try:
            lv   = self.query_one(ListView)
            item = lv.highlighted_child
            if item is None:
                self._close()
                return
            word = item.query_one(Label).renderable
            self._accept(str(word))
        except Exception:
            self._close()

    def _accept(self, word: str) -> None:
        try:
            self._on_select_callback(word)
        except Exception:
            pass
        self._do_remove()

    def _close(self) -> None:
        self._do_remove()

    def _do_remove(self) -> None:
        try:
            self._on_close_callback()
        except Exception:
            pass
        try:
            self.remove()
        except Exception:
            pass
