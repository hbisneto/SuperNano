# tests/conftest.py

import pytest
from pathlib import Path
from unittest.mock import MagicMock
from supernanno.services.app_context import AppContext

@pytest.fixture
def mock_app():
    app = MagicMock()
    app.editor = MagicMock()
    app.editor.text = ""
    app.editor.cursor_location = (0, 0)
    app.editor.language = None
    app.status = MagicMock()
    app.notify = MagicMock()
    app.sidebar = MagicMock()
    app.directory_tree = MagicMock()
    return app

@pytest.fixture
def ctx(mock_app):
    """AppContext mock for testing."""
    context = AppContext(mock_app)
    context.logs = MagicMock()
    context.errors = MagicMock()
    context.status = MagicMock()
    return context