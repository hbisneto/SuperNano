# events/unmount.py

def handle(ctx):
    if getattr(ctx.app, "explicit_file_open", False):
        return

    if ctx.current_path and not ctx.is_dirty:
        ctx.save_session_state(ctx.current_path)