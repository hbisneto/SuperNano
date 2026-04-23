# events/text_area_changed.py

def handle(ctx):
    if getattr(ctx.app, "_loading", False):
        return
    pass