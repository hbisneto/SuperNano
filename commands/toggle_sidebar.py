# commands/toggle_sidebar.py

def execute(ctx):
    sidebar = ctx.app.sidebar
    sidebar.display = not sidebar.display

    ctx.status.info(f"Sidebar Visible: {sidebar.display}")