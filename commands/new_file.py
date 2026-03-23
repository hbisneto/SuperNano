def execute(ctx):
    editor = ctx.editor

    ctx.app._loading = True
    editor.text = ""
    ctx.app._loading = False

    ctx.current_path = None
    ctx.editor_state.mark_saved("")
    ctx.is_dirty = False

    editor.language = None
    editor.focus()

    ctx.status.set("New file (unsaved)")