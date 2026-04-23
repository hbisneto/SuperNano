# events/key.py

def handle(ctx, event):
    state = ctx.state
    
    if ctx.app.in_startup:
        ctx.app.startup_view.display = False
        ctx.app.editor.display = True

        if not ctx.editor.text.strip():
            ctx.editor.load_text(ctx.app.welcome_text)
            ctx.mark_clean()

        ctx.app.editor.focus()
        ctx.app.in_startup = False
        return

    if state and hasattr(state, "handle_key"):
        if state.handle_key(ctx, event):
            return

    if state:
        if event.key == "enter":
            if hasattr(state, "handle_enter"):
                handled = state.handle_enter(ctx)
                if handled:
                    return
        if event.key == "shift+enter":
            if hasattr(state, "prev_match"):
                state.prev_match(ctx)
                return

    if event.key == "escape":
        ctx.clear_pending_action()
        if ctx.state:
            ctx.set_state(None)
            return

        if ctx.path_container and ctx.path_container.display:
            ctx.path_container.display = False
            ctx.app.input_mode = None
            ctx.editor.focus()
            ctx.status.release()
            return

    ctx.status.default()