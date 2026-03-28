# events/mount.py

def handle(ctx):
    if ctx.current_path and ctx.current_path.exists():
        ctx.app.load_file(str(ctx.current_path.absolute()))
    else:
        ctx.app.restore_session()