# events/text_area_changed.py

def handle(ctx):
    """Atualiza o status bar quando o texto do editor muda"""
    app = ctx.app

    # Proteções de segurança
    if getattr(app, '_loading', False) or getattr(app, '_status_locked', False):
        return

    editor = app.get_editor()          # ← mais seguro que ctx.editor

    # Atualiza o estado de "dirty"
    ctx.is_dirty = ctx.editor_state.is_dirty(editor.text)
    dirty_flag = "*" if ctx.is_dirty else ""

    # Linguagem com fallback seguro
    lang = getattr(editor, 'language', None) or "text"

    # Monta o texto do status
    if ctx.current_path is None:
        status_text = f"SuperNanno | {lang} | UTF-8"
    else:
        status_text = f"{ctx.current_path}{dirty_flag} | {lang} | UTF-8"

    # Atualiza usando o método do App (mais estável no momento)
    try:
        app.set_status(status_text)
    except Exception:
        # Fallback direto no widget se o serviço falhar
        try:
            status_widget = app.query_one("#status", expect_type=None)
            if status_widget:
                status_widget.update(status_text)
        except Exception:
            pass  # evita crash total