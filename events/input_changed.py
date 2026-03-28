# events/input_changed.py

def handle(ctx, event):
    state = ctx.state

    if not state:
        return

    if event.input.id == "search_input":
        if hasattr(state, "handle_input"):
            state.handle_input(ctx, event)