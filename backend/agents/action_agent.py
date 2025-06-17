from typing import Dict
from backend.config import Config
from ..agents.error_handler import ErrorHandler
from ..utils.logging_utils import setup_logging
import logging

# Set up logging for this module
setup_logging()
logger = logging.getLogger(__name__)

class ActionRecommenderAgent:
    """
    Agent to recommend moderation actions based on classification results and reasoning.
    """
    def __init__(self):
        self.error_handler = ErrorHandler()
    
    def recommend_action(self, classification: Dict, reasoning: Dict) -> Dict:
        """
        Recommend a moderation action based on the classification label and confidence.
        Adjusts action and severity based on confidence and label.
        """
        try:
            label = classification["label"]
            confidence = classification["confidence"]
            
            # Get base action from mapping in config
            base_action = Config.ACTION_MAPPINGS.get(label, "Flag for human review")
            
            # Adjust action and severity based on confidence and label
            if confidence < 0.7:
                action = "Flag for human review"
                severity = "Low"
            elif label == "Hate" and confidence > 0.9:
                action = "Remove content and ban user immediately"
                severity = "Critical"
            elif label == "Toxic" and confidence > 0.8:
                action = "Remove content and warn user"
                severity = "High"
            elif label == "Offensive":
                action = "Flag for review"
                severity = "Medium"
            elif label == "Neutral":
                action = "Allow content"
                severity = "None"
            else:
                action = base_action
                severity = "Medium"
            
            return {
                "success": True,
                "action": action,
                "severity": severity,
                "confidence": confidence,
                "requires_human_review": confidence < 0.7 or label == "Ambiguous"
            }
            
        except Exception as e:
            # Handle errors gracefully
            return self.error_handler.handle_error(e, "ActionRecommenderAgent.recommend_action")