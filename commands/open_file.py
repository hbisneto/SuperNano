# commands/open_file.py

from pathlib import Path
from textual.widgets import Input

def execute(ctx):
    input_widget = ctx.app.query_one("#path_input", Input)

    # mostra o input
    input_widget.display = True
    input_widget.value = str(Path(".").absolute()) + "/"
    input_widget.focus()

    # 🔥 ESTA LINHA É O BUG
    ctx.app.input_mode = "open"

    # se existir path_container, mostra ele também
    if getattr(ctx.app, "path_container", None):
        ctx.app.path_container.display = True