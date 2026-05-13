# ui/bindings.py

from core import __version__ as VERSION

CSS_FILE = "style.tcss"

BINDINGS = [
    ("ctrl+b", "show_hide_sidebar", "Show/Hide Sidebar"),
    ("ctrl+n", "new_file", "New"),
    ("ctrl+o", "open_path", "Open"),
    ("ctrl+s", "save", "Save"),
    ("ctrl+r", "read_file", "Read File"),
    ("ctrl+f", "search", "Search"),
    ("ctrl+q", "quit", "Quit"),
    ("ctrl+x", "report_issue", "Report Issue"),
    ("f1", "show_settings", "Settings"),
]

SETTINGS_BINDINGS = [
    ("escape", "dismiss", "Close"),
    ("ctrl+s", "save", "Save Settings"),
]

WELCOME = f"""\
# SuperNanno {VERSION.VERSION}

> A modern, extensible terminal-based text editor.


Welcome to SuperNanno — a modern, extensible terminal-based text editor.

SuperNanno is designed to be simple on the surface, yet powerful under the hood.
It combines a clean editing experience with a modular architecture that allows
features like search, file handling, and future extensions through plugins.

Whether you're editing quick notes or building more complex workflows,
SuperNanno aims to stay fast, predictable, and distraction-free.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧠 Core Concepts

• Minimal UI, maximum focus  
  A distraction-free editor that keeps your attention on the text.

• Stateful interactions  
  Features like search operate through controlled states, ensuring consistency.

• Extensible by design  
  Built with a plugin system in mind — allowing future customization of behavior.

• Cross-platform terminal experience  
  Works anywhere your terminal works.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⌨️ Keyboard Shortcuts

CTRL + B   Toggle Sidebar  
CTRL + N   New File  
CTRL + O   Open File  
CTRL + S   Save File  
CTRL + R   Read file (insert content)  
CTRL + F   Search Text  
CTRL + Q   Quit Editor  
F1         Open Settings  

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🚀 Getting Started

• Press CTRL + O to open a file  
• Press CTRL + N to start a new file  
• Start typing to edit immediately  

Use CTRL + F to search within your document.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔌 Future Vision

SuperNanno is evolving toward a fully extensible editor:

• Plugin system for custom behaviors  
• Advanced search strategies (regex, fuzzy, etc.)  
• Automation and workflow extensions  
• UI enhancements and customization  

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Start typing to begin.
"""

IS_WELCOME_TEXT = WELCOME.strip()