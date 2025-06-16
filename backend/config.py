import os
from typing import Dict, Any
from .utils.logging_utils import setup_logging
import logging
from dotenv import load_dotenv

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)

class Config:
    # DIAL API Configuration
    DIAL_API_KEY = os.getenv("your_api_key_here")  # Replace with your actual API key
    DIAL_ENDPOINT = os.getenv("your_api_endpoint_here")  # Replace with your actual API endpoint
    DIAL_API_VERSION = os.getenv("your_api_version_here")  # Replace with your actual API version
    DEPLOYMENT_NAME = "gpt-4o-mini-2024-07-18"
    EMBEDDING_MODEL = "text-embedding-3-small-1"
    
    # Qdrant Configuration
    QDRANT_URL = "localhost"
    QDRANT_PORT = 6333
    COLLECTION_NAME = "policy_data"
    
    # Classification Labels
    CLASSIFICATION_LABELS = ["Hate", "Toxic", "Offensive", "Neutral", "Ambiguous"]
    
    # Action Mappings
    ACTION_MAPPINGS = {
        "Hate": "Remove content and ban user",
        "Toxic": "Remove content and warn user",
        "Offensive": "Flag for review",
        "Neutral": "Allow content",
        "Ambiguous": "Flag for human review"
    }
    
    # Data Paths
    POLICY_DOCS_PATH = "data/policy_data/"