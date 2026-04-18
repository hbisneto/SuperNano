# commands/new_file.py

def execute(ctx):
    editor = ctx.editor
    editor.focus()

    ctx.app._loading = True
    editor.language = None
    editor.load_text("")
    ctx.app._loading = False

    ctx.current_path = None
    ctx.is_dirty = False
    ctx.editor_state.mark_saved("")

    ctx.status.persist("(New file): Untitled")