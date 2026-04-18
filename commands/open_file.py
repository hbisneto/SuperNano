# commands/open_file.py

from pathlib import Path
from textual.widgets import Input

def execute(ctx):
    input_widget = ctx.app.query_one("#path_input", Input)
    input_widget.display = True
    input_widget.value = str(Path(".").absolute()) + "/"
    input_widget.focus()
    ctx.app.input_mode = "open"

    if getattr(ctx.app, "path_container", None):
        ctx.app.path_container.display = True

    ctx.status.persist("(Open): Enter path to open a file or directory")