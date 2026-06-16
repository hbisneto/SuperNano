# supernanno/core/completion.py
import re
from collections import Counter
from typing import List, Tuple

WORD_PATTERN = re.compile(r'\b\w+\b')


class CompletionService:
    """Autocomplete cíclico estilo GNU Nano (simples e confiável)."""

    def __init__(self, ctx):
        self.ctx = ctx
        self._last_prefix: str = ""
        self._completions: List[str] = []
        self._current_index: int = -1

    def get_word_at_cursor(self) -> Tuple[str, int, int]:
        """Retorna (prefixo, row, start_col) da palavra atual."""
        editor = self.ctx.editor
        if not editor:
            return "", 0, 0

        try:
            row, col = editor.cursor_location

            # Pega o texto da linha atual de forma segura
            full_line = editor.document.get_line(row)
            if not full_line:
                full_line = ""

            # Encontra o prefixo (parte da palavra antes do cursor)
            match = re.search(r'(\w*)$', full_line[:col])
            prefix = match.group(1) if match else ""
            start_col = col - len(prefix)

            return prefix, row, start_col
        except Exception:
            return "", 0, 0

    def get_completions(self, text: str, prefix: str) -> List[str]:
        """Retorna sugestões ordenadas."""
        if not prefix or len(prefix) < 1:
            return []

        words = WORD_PATTERN.findall(text)
        freq = Counter(words)

        candidates = [
            w for w in set(words)
            if w.startswith(prefix) and w != prefix
        ]

        candidates.sort(key=lambda w: (-len(w), -freq[w]))
        return candidates[:12]

    def complete(self) -> bool:
        """Executa o autocomplete (cycling)."""
        editor = self.ctx.editor
        if not editor:
            self.ctx.status.warning("(Completion): Editor não disponível")
            return False

        prefix, row, start_col = self.get_word_at_cursor()
        if not prefix:
            self.ctx.status.warning("(Completion): Nenhum prefixo encontrado")
            return False

        full_text = editor.text

        if prefix != self._last_prefix:
            self._completions = self.get_completions(full_text, prefix)
            self._current_index = 0
            self._last_prefix = prefix

        if not self._completions:
            self.ctx.status.warning(f"(Completion): Nenhuma sugestão para '{prefix}'")
            return False

        completion = self._completions[self._current_index]

        try:
            # Substitui o prefixo pela palavra completa
            start = (row, start_col)
            end = (row, start_col + len(prefix))

            editor.replace(completion, start, end)

            # Move o cursor para o final da palavra
            new_col = start_col + len(completion)
            editor.cursor_location = (row, new_col)

            self.ctx.status.info(
                f"(Completion): {completion}  ({self._current_index + 1}/{len(self._completions)})"
            )

            self.ctx.logs.info(
                "(Completion): Applied",
                action="WORD_COMPLETION",
                extra={"prefix": prefix, "completion": completion}
            )

            # Cycling
            self._current_index = (self._current_index + 1) % len(self._completions)
            return True

        except Exception as e:
            self.ctx.errors.handle(e, action="COMPLETION_APPLY")
            self.ctx.status.warning("(Completion): Erro ao aplicar")
            return False