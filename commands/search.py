# commands/search.py

from states.search import SearchState

def execute(ctx):
    ctx.app.set_state(SearchState())

def jump_to(ctx, term: str):
    editor = ctx.app.get_editor()
    text = editor.text

    if not text or not term:
        return False

    index = text.find(term)

    if index == -1:
        ctx.status.set(
            f'Search term not found: "{term}"',
            delay=3,
            status_type="warning"
        )
        return False

    before = text[:index]
    row = before.count("\n")
    last_newline = before.rfind("\n")
    col = index if last_newline == -1 else index - last_newline - 1

    editor.cursor_location = (row, col)
    editor.focus()

    ctx.status.set(
        f'Found: "{term}"',
        delay=2,
        status_type="info"
    )

    return True