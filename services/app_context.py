from pathlib import Path
class AppContext:
    def __init__(self, app):
        self.app = app
        self.current_path: Path | None = None
        self.is_dirty = False
    
    def mark_saved(self):
        self.app._original_text = self.editor.text
        self.is_dirty = False
        
    @property
    def editor(self):
        return self.app.get_editor()
    
    @property
    def status(self):
        return self.app.status

    # @property
    # def is_dirty(self):
    #     return self.app.is_dirty

    # @is_dirty.setter
    # def is_dirty(self, value):
    #     self.app.is_dirty = value