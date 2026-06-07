# states/base.py

class BaseState:
    def on_enter(self, ctx):
        pass

    def on_exit(self, ctx):
        pass

    def handle_input(self, ctx, event):
        pass