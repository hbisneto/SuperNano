"""
Neo Nano Theme

Official SuperNanno default theme.
Inspired by GNU Nano dark palette with modern neon purple/pink accents.

Palette:
- Background: Deep navy (#101820)
- Primary: Purple (#a855f7)
- Accent: Pink (#ec4899)
- Functions: Green (#22c55e)
- Comments: Slate (#64748b)
"""

from rich.style import Style
from textual.widgets.text_area import TextAreaTheme

from .palettes.neo_nano import PALETTE
from .tokens.shared import build_shared_tokens


THEME = TextAreaTheme(
    name="neo_nano",

    base_style=Style(
        bgcolor=PALETTE["background"],
        color=PALETTE["text"]
    ),

    cursor_style=Style(
        color="black",
        bgcolor=PALETTE["string"]
    ),

    selection_style=Style(bgcolor="#312e81"),

    gutter_style=Style(
        bgcolor=PALETTE["background"],
        color="#94a3b8"
    ),

    cursor_line_gutter_style=Style(
        bgcolor="#1f2937",
        color=PALETTE["line_gutter"]
    ),

    cursor_line_style=Style(bgcolor="#1f2937"),

    syntax_styles=build_shared_tokens(PALETTE)
)