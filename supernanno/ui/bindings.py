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
    ("ctrl+g", "complete_word", "Complete Word"),
]

SETTINGS_BINDINGS = [
    ("escape", "dismiss", "Close"),
    ("ctrl+s", "save", "Save Settings"),
]

WELCOME = f"""\
# SuperNanno {VERSION.VERSION}

Nano, but modern.

A modern terminal text editor built with Python, Textual and Tree-sitter.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## About

SuperNanno is a keyboard-driven terminal editor inspired by Nano and rebuilt using modern Python tooling.

Built with:
• Textual
• Tree-sitter
• Rich
• asyncio

Focused on:
• Performance
• Maintainability
• Privacy
• Developer workflows
• Modern terminal UX

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Features

• Tree-sitter syntax highlighting
• Pygments fallback support
• Search & replace engine
• Sidebar explorer
• Session restore
• Backup system
• Structured JSON logging
• Diagnostic reports
• Async config watcher
• Settings UI
• Mouse support
• Cross-platform support
• Offline-first architecture

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Supported Languages

• Python
• JavaScript
• Bash
• Rust
• Go
• JSON
• YAML
• TOML
• Markdown
• HTML
• CSS
• Java
• SQL
• XML
• Regex

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Installation

PyPI:

    pip install supernanno

Developer setup:

    git clone https://github.com/hbisneto/SuperNanno.git
    cd SuperNanno
    bash dev.sh

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Usage

Open file:

    supernanno my_file.py

Open at line:

    supernanno +42 main.py

Search on startup:

    supernanno +/TODO app.py

Read only:

    supernanno -v config.json

Backup mode:

    supernanno -B -C ~/backups/ project.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Keyboard Shortcuts

Ctrl+N  → New file
Ctrl+O  → Open file
Ctrl+S  → Save
Ctrl+F  → Search
Ctrl+H  → Replace
Ctrl+B  → Toggle sidebar
Ctrl+R  → Insert file
Ctrl+X  → Report issue
Ctrl+Q  → Quit
F1       → Settings

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Configuration

.supernannorc example:

    set backup
    set restoresession
    set sidebar
    set tabsize 4
    set indenttype spaces

Runtime settings are available in config.json.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Architecture

SuperNanno uses:

• Event-driven architecture
• Service-oriented design
• Structured logging
• State management
• Async runtime
• Defensive error handling

Core modules:

• core/
• services/
• search/
• handlers/
• events/
• states/
• ui/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Privacy

SuperNanno is privacy-focused.

• No telemetry
• No analytics
• No hidden tracking
• Offline-first
• Local-only configuration and logs

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Running Tests

Run all tests:

    pytest tests/ -v

Specific test:

    pytest tests/test_issue_service.py -v

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Roadmap

Completed:
• Tree-sitter highlighting
• Sidebar explorer
• Structured logging
• Session restore
• Settings UI

Planned:
• Plugin system
• Git integration
• Theme marketplace
• Multi-tab editing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Links

Repository:
https://github.com/hbisneto/SuperNanno

Issues:
https://github.com/hbisneto/SuperNanno/issues

PyPI:
https://pypi.org/project/supernanno/

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Built with care for developers who love the terminal.
"""

IS_WELCOME_TEXT = WELCOME.strip()