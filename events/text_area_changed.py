def handle(ctx):
    app = ctx.app

    if app._loading or app._status_locked:
        return

    editor = ctx.editor

    ctx.is_dirty = ctx.editor_state.is_dirty(editor.text)
    dirty_flag = "*" if ctx.is_dirty else ""

    if ctx.current_path is None:
        app.status.update(f"SuperNanno | {editor.language} | UTF-8")
    else:
        app.status.update(f"{ctx.current_path}{dirty_flag} | {editor.language} | UTF-8")