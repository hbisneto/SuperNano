# events/directory_tree_selected.py

from pathlib import Path

def handle(ctx, event):
    """Quando o usuário seleciona um arquivo no DirectoryTree"""
    path: Path = event.path

    if path.is_file():
        ctx.app.load_file(str(path))
        ctx.status.set(f"Opened: {path.name}", delay=2, status_type="info")
    else:
        # Opcional: se for pasta, você pode expandir ou ignorar
        pass