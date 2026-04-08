# events/mount.py

from pathlib import Path

def handle(ctx):
    app = ctx.app

    # 1) explicit CLI file always wins
    if app.explicit_file_open and ctx.current_path:
        path = Path(ctx.current_path).expanduser()

        if path.exists() and path.is_file():
            app.load_file(str(path), silent=True)
            return

        ctx.status.warning(
            f"(Startup): File not found: {path}",
            delay=3,
            next_text=app.get_default_status()
        )
        return

    # 2) otherwise restore session
    app.restore_session()