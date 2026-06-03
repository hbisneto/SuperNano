# tests/test_services.py

import json
from pathlib import Path
import tempfile
from supernanno.services.config_manager import ConfigManager
from supernanno.services.session_manager import SessionManager
from supernanno.services.rc_parser import parse_rc_file

def test_config_manager_defaults():
    cm = ConfigManager()
    assert cm.get("restoresession") is True
    assert cm.get("tabsize") == 4

def test_rc_parser():
    content = """set tabsize 8
set sidebar
unset backup"""

    with tempfile.TemporaryDirectory() as tmp:
        rc = Path(tmp) / ".supernannorc"
        rc.write_text(content)

        config = parse_rc_file(rc)
        assert config["tabsize"] == 8
        assert config["sidebar"] is True
        assert config["backup"] is False

def test_session_manager():
    with tempfile.TemporaryDirectory() as tmp:
        # Mock from get_config_dir
        import supernanno.services.session_manager as sm
        original = sm.get_config_dir
        sm.get_config_dir = lambda: Path(tmp)

        try:
            session = SessionManager(create_if_missing=True)
            session.set_last_file("/tmp/test.py")
            assert session.get_last_file() == "/tmp/test.py"
        finally:
            sm.get_config_dir = original