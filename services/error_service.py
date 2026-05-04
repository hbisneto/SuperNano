# services/error_service.py
import traceback
from datetime import datetime

class ErrorService:
    """Centraliza tratamento de exceções."""

    def __init__(self, ctx):
        self.ctx = ctx

    def handle(self, exc: Exception, context: str | None = None):
        self.ctx.logs.exception(exc, context)

        self.ctx.last_exception = traceback.format_exc()
        self.ctx.last_exception_type = type(exc).__name__
        self.ctx.last_exception_time = datetime.now()