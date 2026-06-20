# handlers/quit.py

def execute(ctx):
    """Fecha o editor, verificando alterações não salvas."""
    app = ctx.app

    if ctx.is_dirty:
        if getattr(app, "confirm_action", None):
            ctx.mark_clean()
            action = app.confirm_action
            app.confirm_action = None
            action()
            ctx.status.info("(Editor): Changes discarded")
            return

        elif getattr(app, "_confirm_quit", False):
            app.exit()
            return

        else:
            app._confirm_quit = True
            ctx.status.warning("(Editor): Unsaved changes — Press CTRL+Q again to exit")
            return

    app.exit()