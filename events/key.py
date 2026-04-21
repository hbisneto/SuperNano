# events/key.py

def handle(ctx, event):
    state = ctx.state

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
            ctx.editor.focus()
            return

        if ctx.search_container and ctx.search_container.display:
            ctx.search_container.display = False
            ctx.editor.focus()
            return

    ctx.status.default()