def handle(ctx, event):
    state = ctx.state

    if state and hasattr(state, "handle_key"):
        if state.handle_key(ctx, event):
            return

    if state:
        if event.key == "enter":
            if hasattr(state, "next_match"):
                state.next_match(ctx)
                return
        if event.key == "shift+enter":
            if hasattr(state, "prev_match"):
                state.prev_match(ctx)
                return

    if event.key == "escape":
        if ctx.state:
            ctx.app.set_state(None)
            return

        if getattr(ctx.app, 'path_container', None) and ctx.app.path_container.display:
            ctx.app.path_container.display = False
            ctx.app.editor.focus()
            return
        if getattr(ctx.app, 'search_container', None) and ctx.app.search_container.display:
            ctx.app.search_container.display = False
            ctx.app.editor.focus()
            return

        ctx.app.status.update(ctx.app.get_default_status())