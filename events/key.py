def handle(ctx, event):
    state = ctx.state

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

        input_widget = ctx.app.query_one("#path_input")

        if input_widget.display:
            input_widget.display = False
            ctx.editor.focus()