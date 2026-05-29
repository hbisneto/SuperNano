# states/search.py

from states.base import BaseState
from search.controller import SearchController

class SearchState(BaseState):

    def __init__(self):
        self.controller           = SearchController()
        self.current_term:  str   = ""
        self.result               = None
        self.current_match_index  = -1

    @property
    def matches(self) -> list[int]:
        if self.result and self.result.has_matches:
            return self.result.matches
        return []

    def on_enter(self, ctx):
        search_container = ctx.search_container
        if search_container:
            search_container.display = True

        search_bar = ctx.app.search_bar
        if search_bar:
            search_bar.show()
            search_bar.search_input.focus()
            search_bar.hide_replace()

        editor = ctx.editor
        try:
            if hasattr(editor, "cursor_location") and editor.cursor_location:
                cursor = editor.cursor_location
                editor.selection = (cursor, cursor)
        except Exception as e:
            ctx.logs.debug(
                f"(Search): Could not reset editor selection on enter — {e}",
                action="SEARCH_ENTER_RESET_SELECTION",
            )

        self.result              = None
        self.current_term        = ""
        self.current_match_index = -1

        ctx.status.persist("(Search): Find mode — ↓ replace — ESC to cancel")

    def on_exit(self, ctx):
        search_container = ctx.search_container
        if search_container:
            search_container.display = False

        search_bar = ctx.app.search_bar
        if search_bar:
            search_bar.hide()

        ctx.editor.focus()
        ctx.status.release()

    def handle_key(self, ctx, event) -> bool:
        if event.key == "down":
            search_bar = ctx.app.search_bar
            if search_bar:
                search_bar.show_replace()
                if self.current_match_index >= 0:
                    self._go_to_match(ctx)
            ctx.status.persist("(Search): Replace mode — ↑ find only — ESC to cancel")
            return True

        if event.key == "up":
            search_bar = ctx.app.search_bar
            if search_bar:
                search_bar.hide_replace()
            ctx.status.persist("(Search): Find mode — ↓ replace — ESC to cancel")
            return True

        if event.key == "escape":
            ctx.set_state(None)
            return True

        if event.key == "ctrl+h":
            search_bar = ctx.app.search_bar
            if search_bar:
                search_bar.toggle_replace()
            return True

        return False

    def handle_enter(self, ctx) -> bool:
        search_bar = ctx.app.search_bar
        replace_visible = (
            search_bar is not None
            and getattr(search_bar, "replace_input", None) is not None
            and search_bar.replace_input.display
        )

        if replace_visible:
            self.replace_one(ctx)
            self.next_match(ctx)
        else:
            self.next_match(ctx)

        return True

    def handle_input(self, ctx, event):
        if not hasattr(event, "input") or not hasattr(event, "value"):
            return

        input_id = getattr(event.input, "id", None)
        value    = event.value

        if input_id == "search_input":
            self._on_find_changed(ctx, value)

    ###==================== NAVIGATION ====================###

    def next_match(self, ctx):
        if not self.matches:
            return
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self._go_to_match(ctx)

    def prev_match(self, ctx):
        if not self.matches:
            return
        self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        self._go_to_match(ctx)

    ###==================== REPLACE ====================###

    def replace_one(self, ctx, replace_text: "str | None" = None):
        if replace_text is None:
            replace_text = self._get_replace_text(ctx)
            if replace_text is None:
                return

        if self.current_match_index < 0 or not self.matches:
            ctx.status.warning("(Search): No results")
            return

        self._do_replace(ctx, replace_text)

    def replace_all(self, ctx, replace_text: "str | None" = None):
        if replace_text is None:
            replace_text = self._get_replace_text(ctx)
            if replace_text is None:
                return

        if not self.matches or not self.current_term:
            ctx.status.warning("(Search): No results")
            return

        editor   = ctx.editor
        text     = editor.text
        term_len = len(self.current_term)
        count    = len(self.matches)

        for idx in reversed(self.matches):
            text = text[:idx] + replace_text + text[idx + term_len:]

        self._apply_text(editor, text)
        self._find_matches(ctx)
        self.current_match_index = 0 if self.matches else -1

        ctx.status.success(
            f"(Search): Replaced {count}x \"{self.current_term}\" → \"{replace_text}\""
        )

    ###==================== PRIVATE ====================###

    def _apply_match(self, ctx, index: int):
        if not self.matches:
            return

        idx    = self.matches[index]
        term   = self.current_term
        editor = ctx.editor

        start = editor.document.get_location_from_index(idx)
        end   = editor.document.get_location_from_index(idx + len(term))

        editor.cursor_location = start
        editor.selection       = (start, end)

        ctx.status.info(f"(Search): Match {index + 1}/{len(self.matches)} \"{term}\"")

    def _on_find_changed(self, ctx, value: str):
        new_term = value.strip()
        if new_term == self.current_term:
            return

        self.current_term = new_term
        self._find_matches(ctx)
        self.current_match_index = 0 if self.matches else -1
        self._go_to_match(ctx)

    def _find_matches(self, ctx):
        if not self.current_term.strip():
            ctx.status.warning("(Search): Empty search")
            self.result = None
            return

        self.result = self.controller.search(
            ctx.editor.text,
            self.current_term,
        )

        if not self.result or not self.result.has_matches:
            ctx.status.warning(f"(Search): Not found \"{self.current_term}\"")

    def _go_to_match(self, ctx):
        if not self.matches:
            ctx.status.warning(f"(Search): Not found \"{self.current_term}\"")
            return
        self._apply_match(ctx, self.current_match_index)

    def _do_replace(self, ctx, replace_text: str):
        if (
            not self.matches
            or self.current_match_index < 0
            or self.current_match_index >= len(self.matches)
        ):
            return

        idx      = self.matches[self.current_match_index]
        term_len = len(self.current_term)

        editor = ctx.editor
        start  = editor.document.get_location_from_index(idx)
        end    = editor.document.get_location_from_index(idx + term_len)

        editor.replace(
            replace_text,
            start,
            end,
            maintain_selection_offset=False,
        )

        self._find_matches(ctx)

        if self.matches:
            next_index = 0
            for i, match_idx in enumerate(self.matches):
                if match_idx > idx:
                    next_index = i
                    break
            self.current_match_index = next_index
            self._go_to_match(ctx)
        else:
            self.current_match_index = -1

        ctx.status.success(
            f"(Search): Replaced \"{self.current_term}\" → \"{replace_text}\""
        )

    @staticmethod
    def _apply_text(editor, new_text: str):
        doc     = editor.document
        end_loc = doc.get_location_from_index(len(editor.text))
        editor.replace(new_text, (0, 0), end_loc)

    def _get_replace_text(self, ctx) -> "str | None":
        try:
            from textual.widgets import Input
            return ctx.app.query_one("#replace_input", Input).value
        except Exception as e:
            ctx.logs.warning(
                f"(Search): Could not read #replace_input widget — {e}. "
                f"Replace aborted to prevent unintended data loss.",
                action="SEARCH_GET_REPLACE_TEXT",
            )
            ctx.status.warning("(Search): Replace input unavailable — operation cancelled")
            return None
