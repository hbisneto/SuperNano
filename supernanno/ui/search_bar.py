# ui/search_bar.py

from textual.containers import Vertical
from textual.widgets import Input

class SearchBar(Vertical):
    def compose(self):
        self.search_input = Input(placeholder="Find", id="search_input")
        self.replace_input = Input(placeholder="Replace...", id="replace_input")
        
        self.replace_input.display = False
        
        yield self.search_input
        yield self.replace_input

    def show(self):
        self.display = True
        self.search_input.focus()

    def hide(self):
        self.display = False

    def show_replace(self):
        self.replace_input.display = True
        self.replace_input.focus()

    def hide_replace(self):
        self.replace_input.display = False
        self.search_input.focus()

    def toggle_replace(self):
        if self.replace_input.display:
            self.hide_replace()
        else:
            self.show_replace()