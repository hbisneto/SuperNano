# events/list_view_selected.py

from handlers import file

def handle(ctx, event):
    app = ctx.app
    _clear_status(app)

    if not hasattr(event.item, "path"):
        return

    if ctx.is_dirty:
        _handle_dirty(ctx, event)
    else:
        file.load(ctx, str(event.item.path))

def _clear_status(app):
    app.status.remove_class("success")
    app.status.remove_class("info")
    app.status.remove_class("warning")
    app.status.remove_class("error")

def _handle_dirty(ctx, event):
    app = ctx.app

    if app.confirm_action:
        action = app.confirm_action
        app.confirm_action = None
        ctx.mark_clean()
        action()
        return

    app.confirm_action = lambda: app.load_file(str(event.item.path))
    ctx.status.warning("(Editor): Unsaved changes — Click again to discard")