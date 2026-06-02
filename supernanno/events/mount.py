# events/mount.py

from pathlib import Path
from ..events import cursor_watcher
from ..handlers import load


def handle(ctx):
    app = ctx.app

    if not hasattr(app, "_cursor_watcher_running"):
        app._cursor_watcher_running = True
        app.run_worker(cursor_watcher.watch(ctx), name="cursor_watcher")

    if ctx.app.explicit_file_open and ctx.current_path:
        path = Path(ctx.current_path).expanduser()

        if path.exists() and path.is_file():
            load(ctx, str(path), silent=True)
            return

        ctx.current_path = None
        ctx.status.warning(f"(File): Not found \"{path}\"")
        return

    if not ctx.app.explicit_file_open and ctx.restore_session:
        last_file = ctx.session.get_last_file()
        if last_file:
            path = Path(last_file)
            if path.exists() and path.is_file():
                load(ctx, str(path), silent=True)
                ctx.status.info(f"(Session): Restored \"{path.name}\"")

