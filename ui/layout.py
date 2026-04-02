# ui/layout.py

from textual.containers import (
    Horizontal, 
    Vertical
)
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
    """
    Cria e retorna todos os componentes principais da interface.
    Retorna: (header, sidebar, main_content, footer)
    """
    
    # === Sidebar com DirectoryTree ===
    directory_tree = DirectoryTree(path=".", id="sidebar")

    sidebar = Vertical(
        Static("EXPLORER", classes="title"),
        directory_tree,
        id="sidebar"
    )

    # === Input Area (Search + Path Input) ===
    search_bar = SearchBar()
    path_input = Input(
        placeholder="Enter file path or folder...",
        id="path_input"
    )
    path_input.display = False

    input_area = Vertical(
        search_bar,
        path_input,
        id="input_area"
    )
    input_area.display = False

    # === Editor + Status ===
    editor = TextArea.code_editor("", id="editor", language="markdown")
    
    status = Static("SuperNanno Ready", id="status")

    main_content = Vertical(
        editor,
        input_area,
        status,
        id="main"
    )

    # === Header e Footer ===
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
        editor, status
    )