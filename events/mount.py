# events/mount.py

from pathlib import Path
from events import cursor_watcher

def handle(ctx):
    app = ctx.app

    if not hasattr(app, "_cursor_watcher_running"):
        app._cursor_watcher_running = True
        app.run_worker(cursor_watcher.watch(ctx), name="cursor_watcher")

    if app.explicit_file_open and ctx.current_path:
        path = Path(ctx.current_path).expanduser()

        if path.exists() and path.is_file():
            app.load_file(str(path), silent=True)
            return

        ctx.current_path = None
        ctx.status.warning(
            f"(Startup): File not found: {path}",
            delay=3,
            next_text=app.get_default_status()
        )
        return

    app.restore_session()