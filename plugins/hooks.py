# plugins/hooks.py
# This file serves only as documentation + future constants

"""
Nomes de hooks disponíveis para plugins:
- before_new_file
- after_new_file
- before_load
- after_load
- before_save
- after_save
- on_key
- on_status_update
"""

AVAILABLE_HOOKS = {
    "before_new_file",
    "after_new_file",
    "before_load",
    "after_load",
    "before_save",
    "after_save",
    "on_key_pressed",
}