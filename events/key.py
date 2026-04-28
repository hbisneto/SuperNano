# events/key.py

import time

def handle(ctx, event):
    if not hasattr(ctx, "_leader_mode"):
        ctx._leader_mode = False
        ctx._leader_time = 0

    if event.key == "ctrl+k":
        ctx._leader_mode = True
        ctx._leader_time = time.time()
        ctx.status.info("(Plugin): Awaiting key (Ctrl+K)...")
        return

    if ctx._leader_mode and (time.time() - ctx._leader_time > 2):
        ctx._leader_mode = False

    if ctx._leader_mode:
        ctx._leader_mode = False

        handled = ctx.execute_plugin_binding(event.key)

        if not handled:
            ctx.status.warning(f"(Plugin): No action for '{event.key}'")

        return

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