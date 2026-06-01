# events/cursor_watcher.py

import asyncio

_POLL_INTERVAL_NORMAL  = 0.1   # segundos entre verificações normais
_POLL_INTERVAL_IDLE    = 0.2   # quando o editor não tem foco
_BACKOFF_ON_ERROR      = 5.0   # backoff após erro inesperado
_MAX_CONSECUTIVE_ERRORS = 10   # limite de erros antes de parar


async def watch(ctx) -> None:
    """
    Worker assíncrono que monitora a posição do cursor e atualiza
    a status bar.

    Características de resiliência:
    - Nunca morre silenciosamente: erros são logados com stack trace
    - Backoff exponencial após erros consecutivos
    - Para graciosamente após _MAX_CONSECUTIVE_ERRORS erros seguidos
      (evita loop de crash)
    """
    last_pos         = (-1, -1)
    consecutive_errs = 0

    ctx.logs.info(
        "(CursorWatcher): Worker started",
        action="CURSOR_WATCHER_START",
    )

    while True:
        try:
            editor = ctx.editor

            if not editor or not editor.has_focus:
                consecutive_errs = 0  # Reset ao voltar ao idle
                await asyncio.sleep(_POLL_INTERVAL_IDLE)
                continue

            pos = editor.cursor_location

            if pos != last_pos:
                last_pos = pos
                if not ctx.status.is_locked():
                    ctx.status.default()

            consecutive_errs = 0
            await asyncio.sleep(_POLL_INTERVAL_NORMAL)

        except asyncio.CancelledError:
            ctx.logs.info(
                "(CursorWatcher): Worker cancelled",
                action="CURSOR_WATCHER_CANCELLED",
            )
            raise  # Deixa o Textual cancelar o worker normalmente

        except Exception as e:
            consecutive_errs += 1

            ctx.errors.handle(
                e,
                action="CURSOR_WATCHER_ERROR",
                event_origin="cursor_watcher",
                extra={"consecutive_errors": consecutive_errs},
            )

            if consecutive_errs >= _MAX_CONSECUTIVE_ERRORS:
                ctx.logs.critical(
                    f"(CursorWatcher): Worker stopping after {consecutive_errs} "
                    f"consecutive errors. Status bar cursor updates disabled.",
                    action="CURSOR_WATCHER_STOPPED",
                    extra={"consecutive_errors": consecutive_errs},
                )
                return  # Para o worker para não sobrecarregar os logs

            # Backoff antes de tentar novamente
            await asyncio.sleep(_BACKOFF_ON_ERROR)
