# events/directory_tree_selected.py

from pathlib import Path
import traceback

def handle(ctx, event):
    """Quando o usuário seleciona um arquivo no DirectoryTree
    Versão robusta pós-refatoração do Find/Replace."""
    try:
        if hasattr(event, "path"):
            path: Path = event.path
        elif hasattr(event, "item") and hasattr(event.item, "path"):
            path: Path = event.item.path
        else:
            ctx.status.warning("DirectoryTree: evento sem path", delay=3)
            return

        if not path.exists() or not path.is_file():
            ctx.status.warning(f"Not a valid file: {path.name}", delay=3)
            return

        app = ctx.app

        if ctx.is_dirty and not getattr(app, "confirm_action", None):
            app.confirm_action = lambda: app.load_file(str(path))
            ctx.status.warning(
                "File has unsaved changes! Click again to discard."
            )
            return

        if getattr(app, "confirm_action", None):
            app.confirm_action = None

        app.load_file(str(path))

    except Exception as e:
        ctx.status.error(f"Error when opening file from DirectoryTree: {e}", delay=5)
        traceback.print_exc()