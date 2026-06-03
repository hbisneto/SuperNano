# ui/bindings.py

from ..core import __version__ as VERSION

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

## Preview

### Main Editor

![Main Editor](https://raw.githubusercontent.com/hbisneto/hbisneto.github.io/main/supernanno/screenshots/editor_main.png)

A modern terminal editing experience focused on productivity, responsiveness, and developer ergonomics.

---

### Search & Replace

![Search Replace](https://raw.githubusercontent.com/hbisneto/hbisneto.github.io/main/supernanno/screenshots/search_replace.png)

Integrated search engine with literal, case-sensitive, and regex-based search strategies.

---

### Sidebar File Explorer

![Sidebar](https://raw.githubusercontent.com/hbisneto/hbisneto.github.io/main/supernanno/screenshots/sidebar.png)

Quick project navigation with integrated file explorer and click-to-open workflow.

---

### Intelligent Status System

![Status Bar](https://raw.githubusercontent.com/hbisneto/hbisneto.github.io/main/supernanno/screenshots/status_bar.png)

Multi-level status bar with contextual feedback for success, warnings, diagnostics, and runtime events.

---

### Tree-sitter Syntax Highlighting

![Syntax Highlighting](https://raw.githubusercontent.com/hbisneto/hbisneto.github.io/main/supernanno/screenshots/syntax_highlighting.png)

Fast and accurate syntax highlighting powered by Tree-sitter with intelligent Pygments fallback support.

---

## About SuperNanno

**SuperNanno** is a modern terminal-based text editor inspired by Nano, rebuilt from the ground up using contemporary tools, resilient architecture, and developer-focused workflows.

Built in **Python** using the **Textual** framework and **Tree-sitter**, SuperNanno delivers a rich editing experience while preserving the speed, simplicity, and efficiency expected from terminal applications.

The project was designed with long-term maintainability, modularity, and extensibility as core principles.

---

## Key Features

* **Full-featured editor** with advanced cursor movement, selection handling, and smooth scrolling
* **High-performance syntax highlighting** powered by Tree-sitter with support for 16+ languages
* **Intelligent Pygments fallback** for unsupported or partial grammars
* **Robust File Manager** with atomic writes and resilient encoding handling
* **Advanced Search Engine** using Strategy Pattern architecture
* **Session Manager** with automatic restoration and persistence
* **Automatic Backup System** with configurable directories
* **Structured JSON Logging** with correlation IDs and contextual observability
* **Integrated Diagnostic Service** and GitHub report generation
* **Sidebar File Explorer** with responsive navigation
* **Real-time Async Config Watcher**
* **Modern status system** with contextual visual feedback
* **Cross-platform support** for Linux, macOS, and Windows
* **Mouse support** and intuitive keyboard-driven workflows
* **Privacy-first architecture** with primarily offline operation

---

## Supported Languages

SuperNanno currently includes Tree-sitter parsers for:

* Python
* JavaScript
* Bash
* Rust
* Go
* JSON
* YAML
* TOML
* Markdown
* HTML
* CSS
* Java
* SQL
* XML
* Regex

Additional grammars can be integrated in future releases.

---

## Installation

### Development Setup (Recommended)

```bash
git clone https://github.com/hbisneto/SuperNanno.git
cd SuperNanno
bash dev.sh
python app.py
```

The `dev.sh` installer supports:

* Stable channel installation
* Editable development mode
* TestPyPI builds
* Specific version installation
* Local development workflows

---

### PyPI

```bash
pip install supernanno
```

---

## Usage

### Open a file

```bash
supernanno my_file.py
```

### Open at a specific line

```bash
supernanno +42 main.py
```

### Open and search for a term

```bash
supernanno +/TODO app.py
```

### Read-only mode

```bash
supernanno -v config.json
```

### Enable automatic backups

```bash
supernanno -B -C ~/backups/ project.py
```

---

## Keyboard Shortcuts

| Shortcut   | Action                     |
| ---------- | -------------------------- |
| `Ctrl + N` | New file                   |
| `Ctrl + O` | Open file                  |
| `Ctrl + S` | Save file                  |
| `Ctrl + F` | Search                     |
| `Ctrl + H` | Replace                    |
| `Ctrl + B` | Toggle sidebar             |
| `Ctrl + R` | Insert file                |
| `Ctrl + X` | Generate diagnostic report |
| `Ctrl + Q` | Quit editor                |
| `F1`       | Open settings              |

---

## Configuration

SuperNanno is highly configurable through the `.supernannorc` file.

Example:

```bash
set backup
set backupdir ~/.config/Bisneto/SuperNanno/Backup
set restoresession
set sidebar
set tabsize 4
set indenttype spaces
```

Additional runtime and UI settings are available through `config.json`.

---

## Architecture

SuperNanno follows a clean, professional, and maintainable architecture designed for long-term scalability.

#### Core Principles

* **Event-driven architecture**
* **Robust State Management**
* **Service-oriented modular design**
* **Best-effort resilience model**
* **Structured observability**
* **UI-independent business logic**

### Project Structure

```text
├── .gitignore
├── .supernannorc
├── .vscode
│   └── launch.json
├── CODE_OF_CONDUCT.md
├── CONTRIBUTING.md
├── LICENSE
├── README.md
├── config.json
├── dev.sh
├── pyproject.toml
├── requirements.txt
├── setup.py
└── supernanno
    ├── .DS_Store
    ├── __init__.py
    ├── __main__.py
    ├── app.py
    ├── cli
    │   ├── __init__.py
    │   ├── constants.py
    │   ├── models.py
    │   └── parser.py
    ├── core
    │   ├── __init__.py
    │   ├── __version__.py
    │   ├── editor.py
    │   ├── file_manager.py
    │   ├── logger.py
    │   ├── status.py
    │   └── structured_logger.py
    ├── events
    │   ├── __init__.py
    │   ├── button_pressed.py
    │   ├── cursor_watcher.py
    │   ├── directory_tree_selected.py
    │   ├── input_changed.py
    │   ├── input_submitted.py
    │   ├── key.py
    │   ├── list_view_selected.py
    │   ├── mount.py
    │   ├── text_area_changed.py
    │   └── unmount.py
    ├── handlers
    │   ├── __init__.py
    │   ├── file.py
    │   ├── quit.py
    │   └── toggle_sidebar.py
    ├── search
    │   ├── __init__.py
    │   ├── controller.py
    │   ├── engine.py
    │   ├── models.py
    │   ├── registry.py
    │   └── strategies.py
    ├── services
    │   ├── __init__.py
    │   ├── app_context.py
    │   ├── config_applier.py
    │   ├── config_manager.py
    │   ├── error_service.py
    │   ├── issue_service.py
    │   ├── log_service.py
    │   ├── paths.py
    │   ├── rc_parser.py
    │   └── session_manager.py
    ├── states
    │   ├── __init__.py
    │   ├── base.py
    │   └── search.py
    ├── style.tcss
    ├── tests
    │   └── test_issue_service.py
    └── ui
        ├── __init__.py
        ├── bindings.py
        ├── layout.py
        ├── search_bar.py
        ├── settings
        │   ├── __init__.py
        │   └── screen.py
        └── startup_view.py
```

### Architectural Highlights

* `AppContext` as centralized application facade
* Clear separation of concerns
* Async runtime infrastructure
* Structured logging subsystem
* Defensive error handling
* Independent service layers
* Config watcher with exponential backoff resilience

---

## Configuration Directories

| Platform | Directory                                           |
| -------- | --------------------------------------------------- |
| Linux    | `~/.config/Bisneto/SuperNanno/`                     |
| macOS    | `~/Library/Application Support/Bisneto/SuperNanno/` |
| Windows  | `%APPDATA%\Bisneto\SuperNanno\`                     |

---

## Privacy

SuperNanno was built with **privacy as a core principle**.

* Primarily operates offline
* No telemetry
* No unnecessary data collection
* No hidden analytics
* Local-only logs, sessions, and configuration files

---

## Running Tests

```bash
pytest tests/ -v
```

Run a specific test file:

```bash
pytest tests/test_issue_service.py -v
```

---

## Roadmap

* [x] Tree-sitter syntax highlighting
* [x] Sidebar file explorer
* [x] Session persistence
* [x] Structured logging
* [x] Diagnostic reporting
* [x] Async configuration watcher
* [ ] Plugin system
* [ ] Integrated terminal
* [ ] Git integration
* [ ] Theme marketplace
* [ ] Multi-tab editing
* [ ] Package manager

---

## Contributing

Contributions are welcome.

Please read:

* `CONTRIBUTING.md`
* `CODE_OF_CONDUCT.md`

before submitting pull requests or issues.

---

## License

**BSD 3-Clause License**

Copyright © 2026
Heitor Bardemaker A. Bisneto

---

## Acknowledgments

* [Textual](https://github.com/Textualize/textual) — Modern TUI framework
* [Tree-sitter](https://tree-sitter.github.io/tree-sitter/) — Incremental parsing system
* [Rich](https://github.com/Textualize/rich) — Advanced terminal rendering

---

## Links

* Repository:
  https://github.com/hbisneto/SuperNanno

* Issues & Bug Reports:
  https://github.com/hbisneto/SuperNanno/issues

---

**Built with care for developers who ❤️ the terminal.**

"""

IS_WELCOME_TEXT = WELCOME.strip()