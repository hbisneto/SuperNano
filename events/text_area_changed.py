# events/text_area_changed.py

def handle(ctx):
    """Atualiza o status bar quando o texto do editor muda"""
    app = ctx.app

    if getattr(app, '_loading', False) or getattr(app, '_status_locked', False):
        return

    editor = app.get_editor()

    ctx.is_dirty = ctx.editor_state.is_dirty(editor.text)
    dirty_flag = "*" if ctx.is_dirty else ""

    lang = getattr(editor, 'language', None) or "text"

    if ctx.current_path is None:
        status_text = f"SuperNanno | {lang} | UTF-8"
    else:
        status_text = f"{ctx.current_path}{dirty_flag} | {lang} | UTF-8"

    try:
        app.set_status(status_text)
    except Exception:
        try:
            status_widget = app.query_one("#status", expect_type=None)
            if status_widget:
                status_widget.update(status_text)
        except Exception:
            pass