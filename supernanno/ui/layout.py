# ui/layout.py

from .search_bar import SearchBar
from textual.containers import Vertical
from textual.widgets import (
    DirectoryTree,
    Static,
    TextArea,
    Input, 
    Footer, 
    Header
)
from ..ui.startup_view import StartupView
from ..ui.bindings import WELCOME

def create_layout() -> tuple:
    directory_tree = DirectoryTree(path=".", id="directory_tree")
    sidebar = Vertical(
        Static("EXPLORER", classes="title"),
        directory_tree,
        id="sidebar"
    )

    search_bar = SearchBar()
    search_container = Vertical(search_bar, id="search_container")
    search_container.display = False

    path_input = Input(
        placeholder="Enter file path or folder...",
        id="path_input"
    )
    path_container = Vertical(path_input, id="path_container")
    path_container.display = False

    startup_view = StartupView(WELCOME)

    editor = TextArea.code_editor("", id="editor", language="markdown")
    editor.display = False
    status = Static("SuperNanno Ready", id="status")
    

    main_content = Vertical(
        startup_view,
        editor,
        search_container,
        path_container,
        status,
        id="main"
    )

    header = Header()
    footer = Footer()

    return (
        header,
        sidebar,
        main_content,
        footer,
        directory_tree,
        search_bar,
        path_input,
        editor,
        status,
        search_container,
        path_container,
        startup_view
    )