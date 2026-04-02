# ui/search_bar.py

from textual.containers import Horizontal
from textual.widgets import Input

class SearchBar(Horizontal):
    def compose(self):
        self.search_input = Input(placeholder="Find", id="search_input")
        self.replace_input = Input(placeholder="Replace...", id="replace_input")
        yield self.search_input
        yield self.replace_input

    def show(self):
        self.add_class("--visible")
        self.search_input.focus()

    def hide(self):
        self.remove_class("--visible")