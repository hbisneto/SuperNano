# handlers/quit.py

from nannokit.dialogs import messagebox
from . import file

def execute(ctx):
    """Fecha o editor, verificando alterações não salvas."""
    app = ctx.app

    if not ctx.is_dirty:
        app.exit()
        return

    def on_result(result):
        if result == "Yes":
            if ctx.current_path:
                file._do_save(ctx, ctx.current_path)
                app.exit()
            else:
                file.save_as(ctx)
        elif result == "No":
            ctx.mark_clean()
            app.exit()

    messagebox.show(
        "Do you want to save changes before closing?",
        title="Unsaved Changes",
        buttons=messagebox.buttons.YES_NO_CANCEL,
        type=messagebox.type.WARNING,
        callback=on_result,
    )