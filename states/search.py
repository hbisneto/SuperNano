# states/search.py

from textual.widgets import Input
from textual.widgets.text_area import Selection   # opcional, mas recomendado

class SearchState:
    def __init__(self):
        self.current_term = ""
        self.matches = []
        self.current_match_index = -1

    def on_enter(self, ctx):
        """CTRL+F: abre SOMENTE o campo Find"""

        ctx.app.search_container.display = True
        ctx.app.search_bar.show()                    # agora existe novamente
        ctx.app.search_bar.hide_replace()            # garante Replace escondido

        editor = ctx.editor
        if hasattr(editor, 'cursor_location') and editor.cursor_location:
            cursor = editor.cursor_location
            editor.selection = (cursor, cursor)
        else:
            editor.selection = (0, 0)

        self.current_term = ""
        self.matches = []
        self.current_match_index = -1

        ctx.status.set("Find • ↓ to show replace • ESC to cancel")

    def on_exit(self, ctx):
        """Fecha tudo"""
        ctx.app.search_container.display = False
        ctx.app.search_bar.hide()
        ctx.app.editor.focus()
        ctx.status.set(ctx.app.get_default_status())

    def handle_input(self, ctx, event):
        if not hasattr(event, 'input') or not hasattr(event, 'value'):
            return

        input_id = getattr(event.input, 'id', None)
        value = event.value

        if input_id == "search_input":
            new_term = value.strip()
            if new_term != self.current_term:
                self.current_term = new_term
                self._find_matches(ctx)
                self.current_match_index = 0 if self.matches else -1
                self._go_to_match(ctx)

        elif input_id == "replace_input":
            if isinstance(event, Input.Submitted):
                if self.current_match_index >= 0 and self.current_term:
                    self._do_replace(ctx, value)
                    self.next_match(ctx)

    # ==================== NOVO: Controle de expansão com setas ====================
    def handle_key(self, ctx, event):
        """Chamado pelo key.py quando estamos em SearchState"""
        if event.key == "down":
            ctx.app.search_bar.show_replace()
            ctx.status.set("Replace mode • ↑ for Find only • ESC to cancel")
            return True
        elif event.key == "up":
            ctx.app.search_bar.hide_replace()
            ctx.status.set("Find • ↓ to show replace • ESC to cancel")
            return True
        return False

    # (mantenha os métodos _find_matches, _go_to_match, next_match, prev_match, _do_replace iguais)
    def next_match(self, ctx):
        if not self.matches: return
        self.current_match_index = (self.current_match_index + 1) % len(self.matches)
        self._go_to_match(ctx)

    def prev_match(self, ctx):
        if not self.matches: return
        self.current_match_index = (self.current_match_index - 1) % len(self.matches)
        self._go_to_match(ctx)

    def _find_matches(self, ctx):
        text = ctx.editor.text
        term = self.current_term
        if not term:
            self.matches = []
            return
        self.matches = []
        start = 0
        while True:
            idx = text.find(term, start)
            if idx == -1: break
            self.matches.append(idx)
            start = idx + len(term)

    def _go_to_match(self, ctx):
        if not self.matches:
            ctx.status.set(f"Not found: '{self.current_term}'")
            return
        idx = self.matches[self.current_match_index]
        term_len = len(self.current_term)
        editor = ctx.editor

        start_loc = editor.document.get_location_from_index(idx)
        end_loc = editor.document.get_location_from_index(idx + term_len)

        editor.cursor_location = start_loc
        editor.selection = (start_loc, end_loc)

        ctx.status.set(f"Match {self.current_match_index + 1}/{len(self.matches)}: '{self.current_term}'")

    def _do_replace(self, ctx, replace_text):
        if self.current_match_index < 0 or not self.matches:
            return
        idx = self.matches[self.current_match_index]
        term_len = len(self.current_term)
        text = ctx.editor.text

        new_text = text[:idx] + replace_text + text[idx + term_len:]
        ctx.editor.text = new_text

        self._find_matches(ctx)
        if self.matches:
            self.current_match_index = min(self.current_match_index, len(self.matches) - 1)

        ctx.status.set(f"Replaced: '{self.current_term}' --> '{replace_text}'")