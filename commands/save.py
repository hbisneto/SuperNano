def execute(ctx):
    if ctx.current_path:
        try:
            ctx.current_path.write_text(ctx.editor.text, encoding="utf-8")

            ctx.is_dirty = False
            ctx.app._original_text = ctx.editor.text  # 💥 AQUI

            ctx.app.set_status(
                text=f"(Saved): {ctx.current_path.name}",
                delay=3,
                next_text=ctx.app.get_default_status(),
                status_type="success"
            )
        except Exception as e:
            ctx.app.set_status(
                text=f"(Error): {e}",
                delay=3,
                status_type="error"
            )
    else:
        ctx.app.prompt_save_as()