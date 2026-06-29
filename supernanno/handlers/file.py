# handlers/file.py

from pathlib import Path
from textual.widgets import Input
from ..core.file_manager import FileManager
from ..ui.bindings import IS_WELCOME_TEXT


def is_welcome_content(text: str) -> bool:
    return text.strip() == IS_WELCOME_TEXT


def new(ctx):
    current_text = ctx.editor.text

    if is_welcome_content(current_text) or not ctx.is_dirty:
        _do_new(ctx)
        return

    if not ctx.check_dirty_before(lambda: _do_new(ctx)):
        return
    _do_new(ctx)


def _do_new(ctx):
    ctx.app._loading = True
    ctx.editor.load_text("")
    ctx.editor.language = None
    ctx.app._loading = False

    ctx.current_path = None
    ctx.mark_clean()
    ctx.editor.focus()

    ctx.status.persist("(File): New file")
    ctx.logs.info("(File): New file created", action="FILE_NEW")


def open(ctx):
    input_w = ctx.app.query_one("#path_input", Input)
    input_w.display = True
    # input_w.value = str(Path(".").absolute()) + "/"
    input_w.value = str(Path.home()) + "/"
    input_w.focus()

    ctx.app.input_mode = "open"
    if ctx.path_container:
        ctx.path_container.display = True

    ctx.status.persist("(Path): Enter path to open file or folder")


def load(ctx, path_str: str, silent: bool = False):
    path = Path(path_str).expanduser().resolve()

    if path.is_dir():
        try:
            ctx.directory_tree.path = str(path)
            ctx.directory_tree.reload()
            ctx.status.info(f"(Path): Loaded \"{path.name}\"")
            ctx.logs.info(
                f"(File): Directory loaded in tree — {path}",
                action="DIRECTORY_LOAD",
                path=path,
            )
        except Exception as e:
            ctx.errors.handle(
                e,
                action="DIRECTORY_RELOAD",
                path=path,
                event_origin="load",
            )
        return

    if not path.is_file():
        ctx.status.error(f"(File): Not found \"{path}\"")
        ctx.logs.warning(
            f"(File): Path not found or not a file — {path}",
            action="FILE_LOAD_NOT_FOUND",
            path=path,
        )
        return

    def do_load():
        try:
            content = ctx.file_manager.read(path)

            ctx.app._loading = True
            ctx.editor.load_text(content)
            ctx.app._loading = False

            ctx.current_path = path
            ctx.editor.read_only = ctx.read_only
            ctx.mark_clean()
            ctx.set_language(path)
            ctx.save_session_state(path)

            ctx.editor.focus()

            if not silent:
                ctx.status.info(f"(File): Loaded \"{path.name}\"")

            ctx.logs.info(
                f"(File): Loaded successfully — {path.name}",
                action="FILE_LOAD",
                path=path,
            )

            if hasattr(ctx.app, "cli_args") and ctx.app.cli_args:
                cli = ctx.app.cli_args

                if cli.line is not None:
                    ctx.goto_line_column(cli.line, getattr(cli, "column", 0))

                elif cli.search:
                    from ..search.controller import SearchController
                    SearchController().search(ctx, cli.search)

        except UnicodeDecodeError as e:
            ctx.app._loading = False
            ctx.status.error(f"(File): Encoding error — {path.name}")
            ctx.errors.handle(
                e,
                action="FILE_LOAD",
                path=path,
                event_origin="load",
                extra={"tried_encodings": ["utf-8", "latin-1", "cp1252"]},
            )

        except PermissionError as e:
            ctx.app._loading = False
            ctx.status.error(f"(File): Permission denied — {path.name}")
            ctx.errors.handle(
                e,
                action="FILE_LOAD",
                path=path,
                event_origin="load",
            )

        except FileNotFoundError as e:
            ctx.app._loading = False
            ctx.status.error(f"(File): Not found — {path.name}")
            ctx.errors.handle(
                e,
                action="FILE_LOAD",
                path=path,
                event_origin="load",
            )

        except OSError as e:
            ctx.app._loading = False
            ctx.status.error(f"(File): I/O error — {path.name}")
            ctx.errors.handle(
                e,
                action="FILE_LOAD",
                path=path,
                event_origin="load",
            )

        except Exception as e:
            ctx.app._loading = False
            ctx.status.error(f"(File): Load failed — {e}")
            ctx.errors.handle(
                e,
                action="FILE_LOAD",
                path=path,
                event_origin="load",
            )

    if not ctx.check_dirty_before(do_load, "Unsaved changes! Load new file anyway?"):
        return


def read(ctx, value: "str | None" = None):
    if value is None:
        input_w = ctx.app.query_one("#path_input", Input)
        input_w.display = True
        input_w.value = ""
        input_w.placeholder = "Read file into editor..."
        input_w.focus()

        ctx.app.input_mode = "read_file"

        if ctx.path_container:
            ctx.path_container.display = True

        ctx.status.persist("(File): Enter path to insert")
        return

    _do_read(ctx, value)


def _do_read(ctx, value: str):
    path = Path(value).expanduser()

    if not path.exists() or path.is_dir():
        ctx.status.warning(f"(File): Cannot read \"{path}\"")
        ctx.logs.warning(
            f"(File): Cannot read — path does not exist or is directory: {path}",
            action="FILE_READ",
            path=path,
        )
        return

    try:
        content = ctx.file_manager.read(path)
        editor  = ctx.editor
        text    = editor.text

        if editor.selection:
            start, end = editor.selection
            start_i = editor.document.get_index_from_location(start)
            end_i   = editor.document.get_index_from_location(end)

            if start_i > end_i:
                start_i, end_i = end_i, start_i

            new_text  = text[:start_i] + content + text[end_i:]
            new_index = start_i + len(content)
        else:
            index     = editor.document.get_index_from_location(editor.cursor_location)
            new_text  = text[:index] + content + text[index:]
            new_index = index + len(content)

        editor.text            = new_text
        editor.cursor_location = editor.document.get_location_from_index(new_index)

        ctx.status.success(f"(File): Inserted \"{path.name}\"")
        ctx.logs.info(
            f"(File): File inserted at cursor — {path.name}",
            action="FILE_READ",
            path=path,
        )

    except UnicodeDecodeError as e:
        ctx.status.error(f"(File): Encoding error — {path.name}")
        ctx.errors.handle(
            e,
            action="FILE_READ",
            path=path,
            event_origin="read",
        )

    except PermissionError as e:
        ctx.status.error(f"(File): Permission denied — {path.name}")
        ctx.errors.handle(
            e,
            action="FILE_READ",
            path=path,
            event_origin="read",
        )

    except OSError as e:
        ctx.status.error(f"(File): I/O error reading \"{path.name}\"")
        ctx.errors.handle(
            e,
            action="FILE_READ",
            path=path,
            event_origin="read",
        )

    except Exception as e:
        ctx.status.error(f"(File): Insert failed — {e}")
        ctx.errors.handle(
            e,
            action="FILE_READ",
            path=path,
            event_origin="read",
        )


def save(ctx):
    if ctx.read_only:
        ctx.status.warning("(Editor): Cannot save in read-only mode")
        ctx.logs.warning("(File): Save attempted in read-only mode", action="FILE_SAVE_READONLY")
        return

    if ctx.current_path:
        _do_save(ctx, ctx.current_path)
    else:
        save_as(ctx)


def save_as(ctx):
    ctx.app.prompt_save_as()


def _do_save(ctx, path: Path):
    try:
        ctx.file_manager.write(
            path,
            ctx.editor.text,
            backup=ctx.backup_enabled,
            backup_dir=ctx.backup_dir,
        )
        ctx.current_path = path
        ctx.mark_clean()

        if ctx.directory_tree:
            try:
                ctx.directory_tree.reload()
            except Exception as e:
                ctx.logs.warning(
                    f"(File): Directory tree reload failed after save — {e}",
                    action="FILE_SAVE_TREE_RELOAD",
                    path=path,
                )

        ctx.status.success(f"(File): Saved \"{path.name}\"")
        ctx.logs.info(
            f"(File): Saved successfully — {path.name}",
            action="FILE_SAVE",
            path=path,
        )

    except PermissionError as e:
        ctx.status.error(f"(File): Permission denied — {path.name}")
        ctx.errors.handle(
            e,
            action="FILE_SAVE",
            path=path,
            event_origin="ctrl_s",
            extra={
                "content_size": len(ctx.editor.text),
                "backup_enabled": ctx.backup_enabled,
            },
        )

    except IsADirectoryError as e:
        ctx.status.error(f"(File): Path is a directory — {path}")
        ctx.errors.handle(
            e,
            action="FILE_SAVE",
            path=path,
            event_origin="ctrl_s",
        )

    except OSError as e:
        ctx.status.error(f"(File): Save failed — {e}")
        ctx.errors.handle(
            e,
            action="FILE_SAVE",
            path=path,
            event_origin="ctrl_s",
            extra={
                "content_size": len(ctx.editor.text),
                "backup_enabled": ctx.backup_enabled,
            },
        )

    except Exception as e:
        ctx.status.error(f"(File): Save failed — {e}")
        ctx.errors.handle(
            e,
            action="FILE_SAVE",
            path=path,
            event_origin="ctrl_s",
        )
