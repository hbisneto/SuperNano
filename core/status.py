# core/status.py

import asyncio
from datetime import datetime

class StatusService:
    def __init__(self, ctx, debug=False):
        self.ctx = ctx
        self.app = ctx.app

        self.debug_mode = debug
        self.history = []

        self._task = None
        self._locked = False
        self._last_render = None
        self._last_type = None

    # ==================== CORE ==================== #

    def set(self, text, delay=None, next_text=None, status_type="normal", sticky=False):
        if (self._locked or sticky) and delay is None and status_type == "normal":
            return

        if text == self._last_render and status_type == self._last_type:
            return

        status = self.app.status

        if status_type != self._last_type:
            for cls in ("success", "info", "warning", "error"):
                status.remove_class(cls)

            if status_type != "normal":
                status.add_class(status_type)

            self._last_type = status_type

        if text != self._last_render:
            status.update(text)
            self._last_render = text

        self._log(text, status_type)

        if delay:
            self._locked = True

            if self._task:
                self._task.cancel()

            next_text = next_text or self.get_default()

            self._task = self.app.run_worker(
                self._unlock_after(delay, next_text),
                name="status_unlock"
            )

    async def _unlock_after(self, delay, next_text):
        await asyncio.sleep(delay)
        self._locked = False
        self.set(next_text)

    # ==================== HELPERS ==================== #

    def info(self, text, delay=2):
        self.set(text, delay=delay, status_type="info")

    def success(self, text, delay=2):
        self.set(text, delay=delay, status_type="success")

    def warning(self, text, delay=3):
        self.set(text, delay=delay, status_type="warning")

    def error(self, text, delay=4):
        self.set(text, delay=delay, status_type="error")

    def default(self):
        self.set(self.get_default())

    def force(self, text):
        """Ignora lock"""
        self._locked = False
        self.set(text)

    def persist(self, text, status_type="info"):
        """Mensagem persistente até ser liberada manualmente"""
        self._locked = True
        self.set(text, status_type=status_type)

    def release(self):
        """Libera o status persistente e volta ao padrão"""
        self._locked = False
        self.set(self.get_default())

    def is_locked(self):
        return getattr(self, "_locked", False)

    # ==================== DEFAULT ==================== #

    def get_default(self):
        """DELEGADO para o AppContext (nova fonte única de verdade)"""
        return self.ctx.get_default_status()

    # ==================== LOG ==================== #

    def _log(self, text, level):
        entry = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "level": level,
            "message": text,
        }

        self.history.append(entry)

        if self.debug_mode:
            print(f"[{entry['time']}] [{level.upper()}] {text}")