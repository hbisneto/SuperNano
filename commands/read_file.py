# commands/read_file.py

from textual.widgets import Input

def execute(ctx):
    input_widget = ctx.app.query_one("#path_input", Input)

    input_widget.display = True
    input_widget.placeholder = "Enter file path..."
    input_widget.value = ""
    input_widget.focus()

    ctx.app.input_mode = "read_file"