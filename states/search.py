# states/search.py

from textual.widgets import Input
from textual.widgets.text_area import Selection   # opcional, mas recomendado

class SearchState:
    def __init__(self):
        self.current_term = ""
        self.matches = []
        self.current_match_index = -1

    def on_enter(self, ctx):
        ctx.app.search_bar.show()
        ctx.app.search_bar.search_input.value = ""
        ctx.app.search_bar.replace_input.value = ""

        editor = ctx.editor
        if editor.cursor_location:
            cursor = editor.cursor_location
            editor.selection = (cursor, cursor)   # seleção vazia correta
        else:
            editor.selection = (0, 0)

        self.current_term = ""
        self.matches = []
        self.current_match_index = -1

        ctx.app.status.update("Busca ativada • ESC para sair")

    def on_exit(self, ctx):
        """Esconde a barra e retorna foco para o editor."""
        ctx.app.search_bar.hide()
        ctx.app.editor.focus()
        ctx.app.status.update(ctx.app.get_default_status())

    def handle_input(self, ctx, event):
        """Processa mudanças no campo Find e Submit no campo Replace."""
        if not hasattr(event, 'input') or not hasattr(event, 'value'):
            return

        input_id = getattr(event.input, 'id', None)
        value = event.value

        if input_id == "search_input":
            # Busca ao vivo enquanto digita no "Find"
            new_term = value.strip()
            if new_term != self.current_term:
                self.current_term = new_term
                self._find_matches(ctx)
                self.current_match_index = 0 if self.matches else -1
                self._go_to_match(ctx)

        elif input_id == "replace_input":
            # Só faz replace quando o usuário aperta ENTER no campo Replace
            if isinstance(event, Input.Submitted):
                if self.current_match_index >= 0 and self.current_term:
                    self._do_replace(ctx, value)
                    self.next_match(ctx)   # vai para o próximo match automaticamente

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
            if idx == -1:
                break
            self.matches.append(idx)
            start = idx + len(term)

    def _go_to_match(self, ctx):
        if not self.matches:
            ctx.app.status.update(f"Não encontrado: '{self.current_term}'")
            return

        idx = self.matches[self.current_match_index]
        term_len = len(self.current_term)
        editor = ctx.editor

        start_loc = editor.document.get_location_from_index(idx)
        end_loc = editor.document.get_location_from_index(idx + term_len)

        editor.cursor_location = start_loc
        editor.selection = (start_loc, end_loc)

        ctx.app.status.update(
            f"Match {self.current_match_index + 1} de {len(self.matches)}: '{self.current_term}'"
        )

    def _do_replace(self, ctx, replace_text):
        if self.current_match_index < 0 or not self.matches:
            return
        idx = self.matches[self.current_match_index]
        term_len = len(self.current_term)
        text = ctx.editor.text

        new_text = text[:idx] + replace_text + text[idx + term_len:]
        ctx.editor.text = new_text

        # Atualiza matches após a alteração
        self._find_matches(ctx)
        if self.matches:
            self.current_match_index = min(self.current_match_index, len(self.matches) - 1)

        ctx.app.status.update(f"Substituído: '{self.current_term}' → '{replace_text}'")