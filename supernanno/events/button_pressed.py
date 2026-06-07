# events/button_pressed.py

def handle(ctx, event):
    state = ctx.state

    if not state:
        return

    if event.button.id == "next_match":
        if hasattr(state, "next_match"):
            state.next_match(ctx)

    elif event.button.id == "prev_match":
        if hasattr(state, "prev_match"):
            state.prev_match(ctx)

    elif event.button.id == "replace_one":
        if hasattr(state, "replace_one"):
            state.replace_one(ctx)

    elif event.button.id == "replace_all":
        if hasattr(state, "replace_all"):
            state.replace_all(ctx)