# events/input_submitted.py

from pathlib import Path
from handlers import file

def handle(ctx, event):
    if not ctx.app.input_mode:
        return

    value = event.value.strip()
    mode = ctx.app.input_mode

    if mode == "open":
        file.load(ctx, value)

    elif mode == "save":
        if value:
            file._do_save(ctx, Path(value).expanduser().resolve())

    elif mode == "read_file":
        file.read(ctx, value)

    _finalize(ctx)

def _finalize(ctx):
    ctx.app.input_mode = None

    if ctx.path_container and ctx.path_container.display:
        ctx.path_container.display = False

    if ctx.search_container and ctx.search_container.display:
        ctx.search_container.display = False

    ctx.editor.focus()
    ctx.status.release()