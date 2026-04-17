# events/text_area_changed.py

def handle(ctx):
    app = ctx.app

    if getattr(app, '_loading', False) or getattr(app, '_status_locked', False):
        return

    editor = app.get_editor()

    ctx.is_dirty = ctx.editor_state.is_dirty(editor.text)

    status_text = app.get_default_status()

    try:
        app.set_status(status_text)
    except Exception:
        try:
            status_widget = app.query_one("#status", expect_type=None)
            if status_widget:
                status_widget.update(status_text)
        except Exception:
            pass