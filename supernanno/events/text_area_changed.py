# supernanno/events/text_area_changed.py
#
# Handles TextArea.Changed events.
# Additions vs. original:
#   - Calls ctx.completion.on_text_changed(text) to keep the completion
#     index up-to-date incrementally.  The call is defensive and never
#     raises; a broken completion engine must not crash the editor.

def handle(ctx):
    if getattr(ctx.app, "_loading", False):
        return

    text = ctx.editor.text

    ctx.word_count = len(text.split())
    ctx.line_count = text.count("\n") + 1 if text else 0
    ctx.char_count = len(text)

    if "\r\n" in text:
        ctx.eol = "CRLF"
    else:
        ctx.eol = "LF"

    ctx.read_time = max(1, ctx.word_count // 200) if ctx.word_count else 0

    if ctx.current_path and ctx.current_path.exists():
        ctx.file_size = ctx.current_path.stat().st_size
    else:
        ctx.file_size = len(text.encode("utf-8"))

    # ── Completion index update (incremental, defensive) ──────────────
    try:
        if hasattr(ctx, "completion") and ctx.completion is not None:
            ctx.completion.on_text_changed(text)
    except Exception:
        pass  # Completion index failure must never crash the editor

    if not ctx.status.is_locked():
        ctx.status.default()
