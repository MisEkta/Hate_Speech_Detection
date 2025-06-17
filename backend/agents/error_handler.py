import logging
from typing import Dict, Any
import traceback
from ..utils.logging_utils import setup_logging
import logging

# Set up logging for this module
setup_logging()
logger = logging.getLogger(__name__)

class ErrorHandler:
    """
    Handles errors and provides user-friendly error messages for agents.
    """
    def __init__(self):
        logging.basicConfig(level=logging.ERROR)
        self.logger = logging.getLogger(__name__)
    
    def handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """
        Handle errors gracefully and return user-friendly messages.
        Logs the error and returns a structured error response.
        """
        self.logger.error(f"Error in {context}: {str(error)}")
        self.logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Map different error types to user-friendly messages
        error_mappings = {
            "ConnectionError": "Unable to connect to the AI service. Please try again later.",
            "TimeoutError": "The request timed out. Please try again.",
            "JSONDecodeError": "Invalid response format. Please try again.",
            "KeyError": "Missing required data in response.",
            "ValueError": "Invalid input provided."
        }
        
        error_type = type(error).__name__
        user_message = error_mappings.get(error_type, "An unexpected error occurred. Please try again.")
        
        return {
            "success": False,
            "error": True,
            "message": user_message,
            "technical_details": str(error) if context.endswith("debug") else None
        }