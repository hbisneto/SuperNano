# services/app_context.py

from pathlib import Path
from core.editor import EditorState
from core.file_manager import FileManager
from core.status import StatusService
from services.config_manager import ConfigManager
from services.session_manager import SessionManager
from services.config_applier import ConfigApplier

class AppContext:
    def __init__(self, app):
        self.app = app
        self.current_path: Path | None = None
        self.is_dirty = False
        self.state = None
        self.config_watcher = True
        self.config_watcher_interval = 1
        self.restore_session = True
        self.backup_enabled = False
        self.backup_dir = None
        self.read_only = False
        self.path_display = "full"
        self.editor_state = EditorState()
        self.file_manager = FileManager()
        self.status = StatusService(self, debug=True)
        self.config = ConfigManager()
        self.session = SessionManager(
            create_if_missing=not app.explicit_file_open
        )
        self.config_applier = ConfigApplier(self)
    
    def mark_saved(self):
        self.is_dirty = False
        
    @property
    def editor(self):
        return self.app.editor