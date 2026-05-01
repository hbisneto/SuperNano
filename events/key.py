# events/key.py

import time

def handle(ctx, event):
    # ==================== INIT ====================
    if not hasattr(ctx, "_leader_mode"):
        ctx._leader_mode = False
        ctx._leader_sequence = []
        ctx._leader_time = 0

    # ==================== STARTUP ====================
    if ctx.app.in_startup:
        if event.key.lower() == "ctrl+k":
            return

        ctx.app.startup_view.display = False
        ctx.app.editor.display = True

        if not ctx.editor.text.strip():
            ctx.editor.load_text(ctx.app.welcome_text)
            ctx.mark_clean()

        ctx.app.editor.focus()
        ctx.app.in_startup = False
        return

    # ==================== START LEADER (CTRL+K) ====================
    if event.key.lower() == "ctrl+k":
        ctx._leader_mode = True
        ctx._leader_time = time.time()
        ctx._leader_sequence = []

        actions = ctx.get_next_plugin_actions([])
        if actions:
            hints = ", ".join(
                f"{k.upper()} → {cmd if cmd else '(group)'}"
                for k, cmd in actions.items()
            )
            ctx.status.persist(f"(Plugin): Leader mode — {hints}", "info")
        else:
            ctx.status.persist("(Plugin): Leader mode — (no plugins)", "info")

        event.prevent_default()
        event.stop()
        return

    # ==================== TIMEOUT ====================
    if ctx._leader_mode and (time.time() - ctx._leader_time > 3):
        ctx._leader_mode = False
        ctx._leader_sequence = []
        ctx.status.release()
        ctx.status.warning("(Plugin): Leader mode timeout")

    # ==================== MULTI-CHORD / PLUGIN SEQUENCE ====================
    if ctx._leader_mode:
        ctx._leader_time = time.time()

        raw_key = event.key.lower().strip()
        if raw_key.startswith("ctrl+"):
            normalized = raw_key
        elif "+" in raw_key:
            normalized = raw_key.split("+")[-1]
        else:
            normalized = raw_key

        ctx._leader_sequence.append(normalized)

        executed, should_continue = ctx.execute_plugin_sequence(ctx._leader_sequence)

        if executed:
            ctx._leader_mode = False
            ctx._leader_sequence = []
            ctx.status.release()
            ctx.run_pending_plugin_command()
            event.prevent_default()
            event.stop()
            return

        if should_continue:
            hints = ctx.get_next_plugin_actions(ctx._leader_sequence)
            if hints:
                hint_str = ", ".join(
                    f"{k.upper()} → {cmd if cmd else '(group)'}"
                    for k, cmd in hints.items()
                )
                ctx.status.persist(
                    f"(Plugin): {' → '.join(ctx._leader_sequence)} — {hint_str}",
                    "info"
                )
            event.prevent_default()
            event.stop()
            return

        ctx.status.warning(
            f"(Plugin): Unknown sequence — {' + '.join(ctx._leader_sequence)}"
        )
        ctx._leader_mode = False
        ctx._leader_sequence = []
        event.prevent_default()
        event.stop()
        return

    # ==================== ESTADO ATIVO ====================
    state = ctx.state

    if state and hasattr(state, "handle_key"):
        if state.handle_key(ctx, event):
            return

    if state:
        if event.key == "enter":
            if hasattr(state, "handle_enter"):
                if state.handle_enter(ctx):
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