# commands/quit.py

def execute(ctx):
    app = ctx.app

    if ctx.is_dirty:
        if app.confirm_action:
            ctx.is_dirty = False
            action = app.confirm_action
            app.confirm_action = None
            action()
            ctx.status.info("Changes discarded")

        elif getattr(app, "_confirm_quit", False):
            app.exit()

        else:
            app._confirm_quit = True
            ctx.status.warning(
                "Unsaved changes! Press CTRL+Q again to exit."
            )
    else:
        app.exit()