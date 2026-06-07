# tests/test_core.py

from pathlib import Path
import tempfile
from unittest.mock import patch
from supernanno.core.file_manager import FileManager
from supernanno.core.editor import EditorState
from supernanno.services.paths import get_backups_dir

def test_file_manager_read_write():
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "test.txt"
        content = "Olá SuperNanno! 🚀"

        fm = FileManager()
        fm.write(path, content)

        assert path.exists()
        assert fm.read(path) == content

def test_file_manager_backup():
    with tempfile.TemporaryDirectory() as tmp:
        # Mock directory for backups to use the temporary one
        with patch('supernanno.core.file_manager.get_backups_dir') as mock_backup_dir:
            mock_backup_dir.return_value = Path(tmp)

            path = Path(tmp) / "test.py"
            path.write_text("print('hello')")

            fm = FileManager()
            success = fm.create_backup(path)

            assert success is True

            # Verifies if the backup was created
            backups = list(Path(tmp).glob("*.bak"))
            assert len(backups) > 0

def test_editor_state_dirty():
    state = EditorState()
    state.mark_saved("initial")

    assert not state.is_dirty("initial")
    assert state.is_dirty("changed")