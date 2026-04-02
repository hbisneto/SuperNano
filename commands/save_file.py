# commands/save_file.py

from commands import save_as

def execute(ctx):
    if ctx.current_path:
        try:
            ctx.file_manager.write(ctx.current_path, ctx.editor.text)

            ctx.editor_state.mark_saved(ctx.editor.text)
            ctx.is_dirty = False

            ctx.status.set(
                text=f"(Saved): {ctx.current_path.name}",
                delay=3,
                next_text=ctx.app.get_default_status(),
                status_type="success"
            )

        except Exception as e:
            ctx.status.set(
                text=f"(Error): {e}",
                delay=3,
                status_type="error"
            )
    else:
        save_as.execute(ctx)