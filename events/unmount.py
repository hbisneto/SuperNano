# events/unmount.py

def handle(ctx):
    app = ctx.app

    if app.explicit_file_open:
        return

    if ctx.current_path and not ctx.is_dirty:
        app.save_session_state(ctx.current_path)