# events/directory_tree_selected.py

from pathlib import Path

def handle(ctx, event):
    """Quando o usuário seleciona um arquivo no DirectoryTree
    Versão robusta pós-refatoração do Find/Replace."""
    try:
        # Suporte seguro ao atributo do evento (funciona nas duas versões do Textual)
        if hasattr(event, "path"):
            path: Path = event.path
        elif hasattr(event, "item") and hasattr(event.item, "path"):
            path: Path = event.item.path
        else:
            ctx.status.warning("DirectoryTree: evento sem path", delay=3)
            return

        if not path.exists() or not path.is_file():
            ctx.status.warning(f"Não é um arquivo válido: {path.name}", delay=3)
            return

        app = ctx.app

        # Tratamento de arquivo sujo (unsaved changes)
        if ctx.is_dirty and not getattr(app, "confirm_action", None):
            app.confirm_action = lambda: app.load_file(str(path))
            ctx.status.warning(
                "File has unsaved changes! Click again to discard.",
                status_type="warning"
            )
            return

        # Limpa confirmação pendente
        if getattr(app, "confirm_action", None):
            app.confirm_action = None

        # Carrega o arquivo
        app.load_file(str(path))

    except Exception as e:
        ctx.status.error(f"Error when opening file from DirectoryTree: {e}", delay=5)
        import traceback
        traceback.print_exc()