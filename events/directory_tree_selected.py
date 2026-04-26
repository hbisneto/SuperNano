# events/directory_tree_selected.py

from handlers import file

def handle(ctx, event):
    try:
        if hasattr(event, "path"):
            path_str = str(event.path)
        elif hasattr(event, "item") and hasattr(event.item, "path"):
            path_str = str(event.item.path)
        else:
            ctx.status.warning("(Sidebar): Invalid selection")
            return

        file.load(ctx, path_str)

    except Exception as e:
        ctx.status.error(f"(File): Open failed - {e}")