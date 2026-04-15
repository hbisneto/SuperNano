# commands/save_file.py

from commands import save_as

def execute(ctx):
    if ctx.read_only:
        ctx.status.warning(
            "(Read Only): file opened in view mode",
            delay=3
        )
        return
    
    if ctx.current_path:
        try:
            ctx.file_manager.write(
                ctx.current_path,
                ctx.editor.text,
                backup=ctx.backup_enabled,
                backup_dir=ctx.backup_dir
            )

            ctx.editor_state.mark_saved(ctx.editor.text)
            ctx.is_dirty = False

            ctx.status.set(
                text=f"(Saved): {ctx.current_path.name}",
                delay=3,
                next_text=ctx.app.get_default_status(),
                status_type="success"
            )

        except Exception as e:
            ctx.status.error(
                text=f"(Error): {e}",
                delay=3
            )
    else:
        save_as.execute(ctx)