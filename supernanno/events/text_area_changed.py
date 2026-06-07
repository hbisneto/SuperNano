# events/text_area_changed.py

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

    if not ctx.status.is_locked():
        ctx.status.default()