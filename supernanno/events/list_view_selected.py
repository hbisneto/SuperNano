# events/list_view_selected.py

from ..handlers import file
from nannokit.dialogs import messagebox

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
    path = event.item.path

    def on_result(result):
        if result == "Yes":
            ctx.mark_clean()
            file.load(ctx, str(path))

    messagebox.show(
        "Discard unsaved changes and open the selected file?",
        title="Unsaved Changes",
        buttons=messagebox.buttons.YES_NO,
        type=messagebox.type.WARNING,
        callback=on_result,
    )