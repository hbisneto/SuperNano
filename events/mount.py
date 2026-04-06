# events/mount.py

from pathlib import Path

def handle(ctx):
    app = ctx.app

    if ctx.current_path:
        path = Path(ctx.current_path)

        if path.exists() and path.is_file():
            app.load_file(str(path), silent=True)
            return

    app.restore_session()