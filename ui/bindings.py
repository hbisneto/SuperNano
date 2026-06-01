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

**Nano, but modern.**

A powerful, modern terminal text editor built for real developer workflows.

---

# About SuperNanno

**SuperNanno** is a modern terminal-based text editor inspired by Nano, rebuilt from the ground up with contemporary tools and best practices.

Built in **Python** using the **Textual** framework and **Tree-sitter** for fast, accurate syntax highlighting, it delivers a rich feature set while maintaining the speed and lightness of a terminal application.

### Key Features

- **Full-featured editor** with advanced cursor, selection, and smooth scrolling
- **High-performance Syntax Highlighting** powered by **Tree-sitter** (16 languages) with intelligent Pygments fallback
- **Robust File Manager** with atomic writes and comprehensive encoding handling
- **Advanced Search Engine** using Strategy Pattern (literal, case-sensitive, regex)
- **Session Manager** with reliable persistence and automatic restoration
- **Automatic Backup System** with configurable directory
- **Structured JSON Logging** with correlation IDs for observability
- **Diagnostic Service** and integrated **Report Service** for GitHub
- **Sidebar File Explorer** with click-to-open navigation
- **Real-time Async Config Watcher**
- **Intelligent Status Bar** with multiple visual levels
- **Modern UI** with mouse support and intuitive keybindings

---

# Installation

### Development Setup (Recommended)

```bash
git clone https://github.com/hbisneto/SuperNanno.git
cd SuperNanno
bash dev.sh
python app.py
```

The `dev.sh` script automatically handles:

- Virtual environment creation
- Dependency installation
- Initial project setup

### Via PyPI (Coming Soon)

```bash
pip install supernanno
```

---

# Usage

```bash
# Open a file
supernanno my_file.py

# Open at specific line
supernanno +42 main.py

# Open and search for term
supernanno +/TODO app.py

# Read-only mode
supernanno -v config.json

# With backup enabled
supernanno -B -C ~/backups/ project.py
```

---

# Keyboard Shortcuts

| Shortcut          | Action                          |
|-------------------|---------------------------------|
| `Ctrl + N`        | New file                        |
| `Ctrl + O`        | Open file                       |
| `Ctrl + S`        | Save file                       |
| `Ctrl + F`        | Search                          |
| `Ctrl + H`        | Replace All                     |
| `Ctrl + B`        | Toggle Sidebar                  |
| `Ctrl + R`        | Insert file at cursor           |
| `F1`              | Open Settings                   |
| `Ctrl + X`        | Generate Diagnostic Report      |
| `Ctrl + Q`        | Quit (with unsaved protection)  |

---

# Configuration

SuperNanno is highly configurable via the `.supernannorc` file:

```bash
set backup
set backupdir ~/.config/Bisneto/SuperNanno/Backup
set restoresession
set sidebar
set tabsize 4
set indenttype spaces
```

Advanced settings are available in `config.json`.

---

# Architecture

SuperNanno was designed with a clean, professional, and maintainable architecture:

- **Event-driven** design with robust **State Management**
- **AppContext** as the central facade
- Clear separation of concerns (`core`, `services`, `handlers`, `ui`, `events`)
- Structured logging and diagnostic infrastructure
- UI-independent unit tests

Built for long-term maintainability and extensibility.

---

# Configuration Directories

- **Linux**: `~/.config/Bisneto/SuperNanno/`
- **macOS**: `~/Library/Application Support/Bisneto/SuperNanno/`
- **Windows**: `%APPDATA%\Bisneto\SuperNanno\`

---

# Privacy

SuperNanno was built with **privacy as a core principle**:

- Primarily operates offline
- No unnecessary data collection
- No automatic transmission to external servers
- All logs, sessions, and configurations remain local

[Read the full Privacy Policy](privacy.html)

---

# Contributing

Contributions are welcome! Please read our [CONTRIBUTING.md](CONTRIBUTING.md) for details.

---

# License

**BSD-3-Clause License**

Copyright © 2026 Heitor Bardemaker A. Bisneto

---

# Acknowledgments

- [Textual](https://github.com/Textualize/textual) — Outstanding TUI framework
- [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) — High-performance parsing and highlighting

---

**Built with care for developers who ❤️ the terminal.**
"""

IS_WELCOME_TEXT = WELCOME.strip()