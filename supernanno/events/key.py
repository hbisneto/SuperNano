# supernanno/events/key.py
#
# Additions vs. original:
#   - When a completion popup is active, Escape closes it first (before
#     any other state transitions).  This mirrors VS Code behaviour where
#     Esc dismisses the suggestion list without leaving the editor.

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

    # ── Dismiss completion popup first if it is active ────────────────
    if event.key == "escape":
        if hasattr(ctx, "completion") and ctx.completion is not None:
            if ctx.completion.is_active:
                ctx.completion.dismiss()
                event.stop()
                return

    # ── Delegate to active state (Search, etc.) ───────────────────────
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
