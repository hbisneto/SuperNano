# commands/search.py

from states.search import SearchState

def execute(ctx):
    ctx.app.set_state(SearchState())