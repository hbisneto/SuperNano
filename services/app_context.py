class AppContext:
    def __init__(self, app):
        self.app = app
        self.editor = None
        self.status = None
        self.current_path = None
        self.is_dirty = False