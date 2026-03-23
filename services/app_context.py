from pathlib import Path
from core.editor import EditorState
from core.file_manager import FileManager
from core.status import StatusService
class AppContext:
    def __init__(self, app):
        self.app = app
        self.current_path: Path | None = None
        self.is_dirty = False

        self.editor_state = EditorState()
        self.file_manager = FileManager()
        self.status = StatusService(app, debug=True)
    
    def mark_saved(self):
        self.is_dirty = False
        
    @property
    def editor(self):
        return self.app.get_editor()