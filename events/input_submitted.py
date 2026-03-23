from pathlib import Path


def handle(ctx, event):
    value = event.value
    mode = ctx.app.input_mode

    handler = HANDLERS.get(mode, _handle_open)
    handler(ctx, event, value)

    _finalize(ctx, event)


# =========================
# HANDLERS
# =========================

def _handle_read_file(ctx, event, value):
    path = Path(value).expanduser()

    if not path.exists():
        ctx.status.set(f"File not found: {path}", delay=3, status_type="error")
        return

    if path.is_dir():
        ctx.status.set(f"Cannot read a directory: {path}", delay=3, status_type="warning")
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
        editor.cursor_location = editor.document.get_location_from_index(new_index)

        ctx.status.set(f"(Inserted): {path}", delay=3, status_type="success")

    except Exception as e:
        ctx.status.set(f"(Error): {e}", delay=3, status_type="error")


def _handle_search(ctx, event, value):
    editor = ctx.editor
    index = editor.text.find(value)

    if index != -1:
        editor.cursor_location = editor.document.get_location_from_index(index)
        ctx.app.status.update(f"Found: {value}")
    else:
        ctx.app.status.update("Not found")


def _handle_save(ctx, event, value):
    path = Path(value).expanduser()

    try:
        ctx.file_manager.write(path, ctx.editor.text)

        ctx.current_path = path
        ctx.editor_state.mark_saved(ctx.editor.text)
        ctx.is_dirty = False

        ctx.status.set(
            text=f"(Saved): {path.name}",
            delay=3,
            next_text=ctx.app.get_default_status(),
            status_type="success"
        )

        ctx.app.refresh_file_list()

    except Exception as e:
        ctx.status.set(
            text=f"(Error): {e}",
            delay=5,
            status_type="error"
        )


def _handle_open(ctx, event, value):
    path = Path(value).expanduser()

    if path.exists():
        ctx.app.load_file(str(path))
        ctx.editor.focus()
    else:
        ctx.app.status.update("File not found")

HANDLERS = {
    "read_file": _handle_read_file,
    "search": _handle_search,
    "save": _handle_save,
}


# =========================
# FINALIZATION
# =========================

def _finalize(ctx, event):
    ctx.app.input_mode = None
    event.input.display = False