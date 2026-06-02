# events/directory_tree_selected.py

from ..handlers import file


def handle(ctx, event) -> None:
    try:
        if hasattr(event, "path"):
            path_str = str(event.path)
        elif hasattr(event, "item") and hasattr(event.item, "path"):
            path_str = str(event.item.path)
        else:
            ctx.status.warning("(Sidebar): Invalid selection")
            ctx.logs.warning(
                "(Sidebar): Directory tree event has no path attribute",
                action="SIDEBAR_SELECT",
            )
            return

        file.load(ctx, path_str)

    except Exception as e:
        ctx.status.error(f"(File): Open failed — {e}")
        ctx.errors.handle(
            e,
            action="SIDEBAR_FILE_OPEN",
            event_origin="sidebar_click",
        )
