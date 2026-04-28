# plugins/hooks.py
# Documentação e constantes dos hooks disponíveis para plugins.

"""
Hooks disponíveis para plugins registrarem callbacks:

  Ciclo de vida de arquivo:
    before_new_file   — antes de criar novo arquivo
    after_new_file    — após criar novo arquivo
    before_load       — antes de carregar um arquivo
    after_load        — após carregar um arquivo
    before_save       — antes de salvar
    after_save        — após salvar com sucesso

  Editor:
    on_key_pressed    — a cada tecla pressionada (recebe key event)

  Search (já disparados em states/search.py):
    before_search     — antes de executar uma busca
    after_search      — após executar uma busca (recebe SearchResult)
"""

AVAILABLE_HOOKS = {
    "before_new_file",
    "after_new_file",
    "before_load",
    "after_load",
    "before_save",
    "after_save",
    "on_key_pressed",
    "before_search",
    "after_search",
}
