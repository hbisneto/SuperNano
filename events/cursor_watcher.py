# events/cursor_watcher.py

import asyncio

async def watch(ctx):
    last_pos = (-1, -1)

    while True:
        editor = ctx.editor
        if not editor or not editor.has_focus:
            await asyncio.sleep(0.2)
            continue

        pos = editor.cursor_location
        if pos != last_pos:
            last_pos = pos
            if not ctx.status.is_locked():
                ctx.status.default()

        await asyncio.sleep(0.1)