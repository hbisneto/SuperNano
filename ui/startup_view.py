# ui/startup_view.py

from textual.containers import Container
from textual.containers import VerticalScroll
from textual.widgets import Markdown

class StartupView(Container):
    def __init__(self, content: str):
        super().__init__()
        self.content = content

    def compose(self):
        yield VerticalScroll(Markdown(self.content))