# ui/layout.py

from textual.containers import Vertical
from textual.widgets import (
    DirectoryTree,
    Static,
    TextArea,
    Input, 
    Footer, 
    Header
)

from .search_bar import SearchBar

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

    editor = TextArea.code_editor("", id="editor", language="markdown")
    status = Static("SuperNanno Ready", id="status")
    

    main_content = Vertical(
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
        path_container
    )