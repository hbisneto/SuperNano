from rich.style import Style
from textual.widgets.text_area import TextAreaTheme

from .palettes.vscode import PALETTE
from .tokens.shared import build_shared_tokens


THEME = TextAreaTheme(
    name="vscode",

    base_style=Style(
        bgcolor=PALETTE["background"],
        color=PALETTE["text"]
    ),

    cursor_style=Style(
        color="black",
        bgcolor="#AEAFAD"
    ),

    selection_style=Style(
        bgcolor="#264F78"
    ),

    gutter_style=Style(
        bgcolor=PALETTE["background"],
        color="#858585"
    ),

    cursor_line_gutter_style=Style(
        bgcolor="#2A2D2E",
        color="#C8C8C8"
    ),

    cursor_line_style=Style(
        bgcolor="#2A2D2E"
    ),

    syntax_styles=build_shared_tokens(PALETTE)
)