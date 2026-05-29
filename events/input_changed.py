# events/input_changed.py

def handle(ctx, event):
    state = ctx.state

    if not state:
        return

    input_id = getattr(event.input, "id", None)

    if input_id in ("search_input", "replace_input"):
        if hasattr(state, "handle_input"):
            state.handle_input(ctx, event)
