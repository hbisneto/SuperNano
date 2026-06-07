# tests/test_cli.py

import sys
from unittest.mock import patch
from supernanno.cli.parser import parse_cli_args

def test_parse_help():
    with patch.object(sys, 'argv', ['supernanno', '--help']):
        args = parse_cli_args()
        assert args.help is True

def test_parse_version():
    with patch.object(sys, 'argv', ['supernanno', '--version']):
        args = parse_cli_args()
        assert args.version is True

def test_parse_view_mode():
    with patch.object(sys, 'argv', ['supernanno', '-v', 'file.txt']):
        args = parse_cli_args()
        assert args.view_mode is True
        assert args.file == 'file.txt'

def test_parse_backup():
    with patch.object(sys, 'argv', ['supernanno', '-B', 'file.py']):
        args = parse_cli_args()
        assert args.backup is True
        assert args.file == 'file.py'

def test_parse_line_and_column():
    with patch.object(sys, 'argv', ['supernanno', '+42,15', 'main.py']):
        args = parse_cli_args()
        assert args.line == 42
        assert args.column == 15
        assert args.file == 'main.py'

def test_parse_search():
    with patch.object(sys, 'argv', ['supernanno', '+/TODO', 'app.py']):
        args = parse_cli_args()
        assert args.search == 'TODO'
        assert args.file == 'app.py'

def test_invalid_option():
    with patch.object(sys, 'argv', ['supernanno', '--invalid']):
        args = parse_cli_args()
        assert args.invalid_arg == '--invalid'