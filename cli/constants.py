from core.__version__ import VERSION

VERSION = f"""Bisneto SuperNanno, version {VERSION}
(C) 2026 Bisneto."""

CLI_OPTIONS = [
  ("-h", "--help", "Show this help text and exit"),
  ("-V", "--version", "Print version information and exit"),
  ("-v", "--view", "Open file in read-only mode"),
  ("-B", "--backup", "Save backups of existing files"),
  ("-C <dir>", "--backupdir=<dir>", "Directory for backup files"),
]

def build_help():
  lines = [
    "Usage: supernanno [OPTIONS] [[+LINE[,COLUMN] | +/SEARCH] FILE]",
    "",
    "To place the cursor on a specific line of a file, put the line number with",
    "a '+' before the filename. The column number can be added after a comma.",
    "To search after opening, use +/SEARCH before the filename.",
    "",
    " Option         Long option             Meaning",
  ]

  for short, long, desc in CLI_OPTIONS:
    lines.append(f" {short:<14} {long:<23} {desc}")

  return "\n".join(lines)

HELP_TEXT = build_help()

# HELP_TEXT = """\
# SuperNanno - Nano, but modern and with extra features.

# Usage:
#   supernanno [OPTIONS] [[+LINE[,COLUMN] | +/SEARCH] FILE]

# Options:
#   --help          Show this help message and exit
#   --version       Show version information and exit

# Nano-style:
#   +LINE           Open file at line
#   +LINE,COLUMN    Open file at line and column
#   +/SEARCH        Search term after opening file

# Examples:
#   supernanno file.txt
#   supernanno +25 file.txt
#   supernanno +25,8 file.txt
#   supernanno +/TODO app.py
# """