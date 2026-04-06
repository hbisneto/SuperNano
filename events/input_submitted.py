# events/input_submitted.py

from pathlib import Path

def handle(ctx, event):
    if ctx.state:
        ctx.state.handle_input(ctx, event)
        return

    value = event.value
    mode = ctx.app.input_mode

    handler = HANDLERS.get(mode, _handle_open)
    handler(ctx, event, value)

    _finalize(ctx, event)

###==================== HANDLERS ====================###

def _handle_read_file(ctx, event, value):
    path = Path(value).expanduser()
    if not path.exists():
        ctx.status.warning(f"File not found: {path}", delay=3, status_type="error")
        return
    if path.is_dir():
        ctx.status.warning(f"Cannot read a directory: {path}", delay=3, status_type="warning")
        return

    try:
        content = ctx.file_manager.read(path)
        editor = ctx.editor
        text = editor.text

        if editor.selection:
            start, end = editor.selection
            start_i = editor.document.get_index_from_location(start)
            end_i = editor.document.get_index_from_location(end)
            if start_i > end_i:
                start_i, end_i = end_i, start_i
            new_text = text[:start_i] + content + text[end_i:]
            new_index = start_i + len(content)
        else:
            cursor = editor.cursor_location
            index = editor.document.get_index_from_location(cursor)
            new_text = text[:index] + content + text[index:]
            new_index = index + len(content)

        editor.text = new_text
        editor.cursor_location = editor.document.get_index_from_location(new_index)
        ctx.status.success(f"(Inserted): {path}", delay=3)
    except Exception as e:
        ctx.status.error(f"(Error): {e}", delay=3)

def _handle_open(ctx, event, value):
    path = Path(value).expanduser().resolve()

    if not path.exists():
        ctx.status.error(f"(Error) - Path not found: {path}", delay=3)
        return

    app = ctx.app

    if path.is_file():
        app.load_file(str(path))
        app.editor.focus()
    elif path.is_dir():
        app.directory_tree.path = str(path)
        app.directory_tree.reload()
        ctx.status.info(f"(Loaded folder): {path.name}", delay=2)
    else:
        ctx.status.warning("Not a file or folder", delay=3)

def _handle_save(ctx, event, value):
    path = Path(value).expanduser()
    try:
        ctx.file_manager.write(path, ctx.editor.text)
        ctx.current_path = path
        ctx.editor_state.mark_saved(ctx.editor.text)
        ctx.is_dirty = False
        ctx.status.set(f"(Saved): {path.name}", delay=3, next_text=ctx.app.get_default_status(), status_type="success")
        ctx.app.directory_tree.reload()
    except Exception as e:
        ctx.status.error(f"(Error): {e}", delay=5)


HANDLERS = {
    "read_file": _handle_read_file,
    "save": _handle_save,
}

###==================== FINALIZATION ====================###

def _finalize(ctx, event):
    ctx.app.input_mode = None

    if hasattr(ctx.app, "path_container"):
        ctx.app.path_container.display = False

    if hasattr(ctx.app, "search_container"):
        ctx.app.search_container.display = False

    ctx.editor.focus()