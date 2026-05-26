# states/search.py

from states.base import BaseState
from search.controller import SearchController

_HISTORY_MAX = 20


class SearchState(BaseState):

    def __init__(self):
        self.controller          = SearchController()
        self.current_term:  str  = ""
        self.matches:  list[int] = []
        self.current_match_index = -1
        self.result              = None
        # ── Histórico de termos pesquisados ───────────────────────────
        self.search_history: list[str] = []

    ###==================== BASE STATE ====================###

    def on_enter(self, ctx):
        search_container = ctx.search_container
        if search_container:
            search_container.display = True

        search_bar = ctx.app.search_bar
        if search_bar:
            search_bar.show()

        ctx.status.persist(
            "(Search): Type to search — ↓ show Replace, ↑ hide Replace, "
            "Enter: next/replace, Shift+Enter: prev, Esc: exit"
        )

    def on_exit(self, ctx):
        search_container = ctx.search_container
        if search_container:
            search_container.display = False

        search_bar = ctx.app.search_bar
        if search_bar:
            search_bar.hide()
            # Garante que o replace fique escondido ao fechar
            try:
                search_bar.hide_replace()
            except Exception:
                pass

        ctx.status.release()

    def handle_key(self, ctx, event) -> bool:
        key = event.key

        if key == "escape":
            ctx.set_state(None)
            return True

        if key == "ctrl+h":
            search_bar = ctx.app.search_bar
            if search_bar:
                search_bar.toggle_replace()
            return True

        # ── Seta para baixo: mostra Replace e foca nele ───────────────
        if key == "down":
            search_bar = ctx.app.search_bar
            if search_bar:
                try:
                    search_bar.show_replace()
                    ctx.logs.debug(
                        "(Search): Replace panel shown via ↓",
                        action="SEARCH_SHOW_REPLACE",
                    )
                except Exception as e:
                    ctx.errors.handle(
                        e,
                        action="SEARCH_SHOW_REPLACE",
                        event_origin="key_down",
                    )
            return True

        # ── Seta para cima: esconde Replace e volta foco ao Find ──────
        if key == "up":
            search_bar = ctx.app.search_bar
            if search_bar:
                try:
                    search_bar.hide_replace()
                    ctx.logs.debug(
                        "(Search): Replace panel hidden via ↑",
                        action="SEARCH_HIDE_REPLACE",
                    )
                except Exception as e:
                    ctx.errors.handle(
                        e,
                        action="SEARCH_HIDE_REPLACE",
                        event_origin="key_up",
                    )
            return True

        return False

    def handle_enter(self, ctx) -> bool:
        """
        Comportamento do Enter:
        - Replace visível → executa replace_one() e depois next_match()
        - Replace oculto  → vai para a próxima ocorrência
        Também salva o termo atual no histórico.
        """
        self._save_to_history(ctx)

        search_bar = ctx.app.search_bar
        replace_visible = False

        if search_bar:
            try:
                replace_visible = bool(search_bar.replace_input.display)
            except Exception as e:
                ctx.logs.debug(
                    f"(Search): Could not read replace_input.display — {e}",
                    action="SEARCH_ENTER_CHECK_REPLACE",
                )

        if replace_visible:
            self.replace_one(ctx)
        else:
            self.next_match(ctx)

        return True

    def handle_input(self, ctx, event):
        if event.input.id == "search_input":
            self._on_find_changed(ctx, event.value)

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

    ###==================== HISTORY ====================###

    def _save_to_history(self, ctx):
        """
        Salva o termo atual no histórico de buscas.
        - Ignora termos vazios.
        - Remove duplicata recente (mesmo termo já no topo não é re-inserido).
        - Limita a _HISTORY_MAX entradas.
        """
        term = self.current_term.strip()
        if not term:
            return

        try:
            # Remove ocorrência anterior do mesmo termo (sem duplicatas)
            if term in self.search_history:
                self.search_history.remove(term)

            self.search_history.insert(0, term)

            # Garante tamanho máximo
            if len(self.search_history) > _HISTORY_MAX:
                self.search_history = self.search_history[:_HISTORY_MAX]

            ctx.logs.debug(
                f"(Search): Term added to history — \"{term}\" "
                f"({len(self.search_history)} items)",
                action="SEARCH_HISTORY_SAVE",
            )

        except Exception as e:
            ctx.errors.handle(
                e,
                action="SEARCH_HISTORY_SAVE",
                event_origin="handle_enter",
            )

    ###==================== REPLACE ====================###

    def replace_one(self, ctx, replace_text: "str | None" = None):
        if replace_text is None:
            replace_text = self._get_replace_text(ctx)
            if replace_text is None:
                return  # _get_replace_text já logou o problema

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
        """
        Lê o texto do widget replace_input.

        Retorna a string (pode ser vazia se o usuário não digitou nada).
        Retorna None se o widget não existe ou está desmontado —
        neste caso loga WARNING e aborta o replace para evitar
        deleção silenciosa de conteúdo.
        """
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
