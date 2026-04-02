# events/unmount.py

def handle(ctx):
    if ctx.current_path and not ctx.is_dirty:
        ctx.app.save_session_state(ctx.current_path)