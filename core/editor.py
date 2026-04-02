# core/editor.py

class EditorState:
    def __init__(self):
        self.original_text = ""

    def mark_saved(self, text):
        self.original_text = text

    def is_dirty(self, text):
        return text != self.original_text