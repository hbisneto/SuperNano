def handle(ctx, event):
    if event.key == "escape":
        input_widget = ctx.app.query_one("#path_input")
        
        if input_widget.display:
            input_widget.display = False
            ctx.editor.focus()