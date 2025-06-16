import os
from typing import Dict, Any
from .utils.logging_utils import setup_logging
import logging

setup_logging()
logger = logging.getLogger(__name__)

class Config:
    # DIAL API Configuration
    DIAL_API_KEY = "dial-umhniqw84p8dja00xqa41xx776q"
    DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
    DIAL_API_VERSION = "2024-02-01"
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