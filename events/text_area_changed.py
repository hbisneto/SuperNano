# events/text_area_changed.py

def handle(ctx):
    if getattr(ctx.app, "_loading", False):
        return

    editor = ctx.editor
    ctx.is_dirty = ctx.editor_state.is_dirty(editor.text)