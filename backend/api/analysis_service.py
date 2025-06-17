from datetime import datetime
from typing import Dict, List, Optional

from ..agents.hate_speech_agent import HateSpeechDetectionAgent
from ..agents.retriever_agent import HybridRetrieverAgent
from ..agents.reasoning_agent import PolicyReasoningAgent
from ..agents.action_agent import ActionRecommenderAgent
from ..utils.logging_utils import setup_logging
import logging

# Set up logging for this module
setup_logging()
logger = logging.getLogger(__name__)

# Initialize all agents for analysis
hate_speech_agent = HateSpeechDetectionAgent()
retriever_agent = HybridRetrieverAgent()
reasoning_agent = PolicyReasoningAgent()
action_agent = ActionRecommenderAgent()

def analyze_text_service(text: str, include_policies: bool = True, include_reasoning: bool = True) -> Dict:
    """
    Analyze text for hate speech and policy violations.
    Steps:
    1. Classify the text.
    2. Retrieve relevant policies (if requested).
    3. Generate reasoning (if requested).
    4. Recommend moderation action.
    Returns a dictionary with all results.
    """
    logger.info("Starting analysis service for text input")
    # Step 1: Classification
    classification_result = hate_speech_agent.classify_text(text)
    if not classification_result["success"]:
        logger.error(f"Classification failed: {classification_result['message']}")
        raise Exception(classification_result["message"])
    
    response_data = {
        "classification": classification_result,
        "timestamp": datetime.now().isoformat()
    }
    
    # Step 2: Retrieve policies (if requested)
    if include_policies:
        logger.info("Retrieving relevant policies")
        retrieval_result = retriever_agent.retrieve_policies(
            text, 
            classification_result["label"]
        )
        if retrieval_result["success"]:
            response_data["retrieved_policies"] = retrieval_result["documents"]
    
    # Step 3: Generate reasoning (if requested)
    if include_reasoning:
        logger.info("Generating reasoning for classification")
        reasoning_result = reasoning_agent.generate_reasoning(
            text,
            classification_result,
            response_data.get("retrieved_policies", [])
        )
        if reasoning_result["success"]:
            response_data["reasoning"] = reasoning_result["reasoning"]
    
    # Step 4: Recommend action
    logger.info("Recommending action based on classification and reasoning")
    action_result = action_agent.recommend_action(
        classification_result,
        reasoning_result if include_reasoning else {}
    )
    if action_result["success"]:
        response_data["recommended_action"] = action_result
    
    logger.info("Analysis service completed successfully")
    return response_data