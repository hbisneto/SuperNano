# services/error_service.py

import traceback
from datetime import datetime

class ErrorService:
    def __init__(self, ctx):
        self.ctx = ctx

    def handle(self, exc: Exception) -> None:
        trace = traceback.format_exc()

        self.ctx.logs.error(trace)
        self.ctx.last_exception      = trace
        self.ctx.last_exception_type = type(exc).__name__
        self.ctx.last_exception_time = datetime.now()

        if not self.ctx.status.is_locked():
            self.ctx.status.error(
                f"{self.ctx.last_exception_type} occurred — press CTRL+X to report"
            )

        try:
            self.ctx.app.notify(
                "An error occurred. Press CTRL+X to report this issue.",
                title="Error",
                severity="error",
                timeout=10,
            )
        except Exception:
            # notify() must never cause a secondary crash.
            pass