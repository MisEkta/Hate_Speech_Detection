import pytest
from backend.agents.error_handler import ErrorHandler

def test_handle_error_connection():
    """
    Test that handle_error returns a structured error response for a generic exception.
    """
    handler = ErrorHandler()
    class DummyError(Exception): pass
    error = DummyError("fail")
    result = handler.handle_error(error, "test context")
    assert result["success"] is False
    assert "message" in result