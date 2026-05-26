# events/input_changed.py

def handle(ctx, event):
    state = ctx.state

    if not state:
        return

    # Propaga mudanças tanto do search_input quanto do replace_input
    if event.input.id in ("search_input", "replace_input"):
        if hasattr(state, "handle_input"):
            state.handle_input(ctx, event)
