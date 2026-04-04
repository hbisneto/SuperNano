# events/directory_tree_selected.py

from pathlib import Path


def handle(ctx, event):
    path = Path(event.path)

    if not path.exists() or not path.is_file():
        return

    app = ctx.app

    if ctx.is_dirty:
        if app.confirm_action:
            action = app.confirm_action
            app.confirm_action = None
            ctx.is_dirty = False
            action()
            return

        app.confirm_action = lambda: app.load_file(str(path))
        ctx.status.set(
            "File has unsaved changes! Click again to discard.",
            status_type="warning"
        )
        return

    app.load_file(str(path))
    # ctx.status.set(f"Opened: {path.name}", delay=2, status_type="info")