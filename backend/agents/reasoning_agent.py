from openai import AzureOpenAI
from typing import Dict, List
from backend.config import Config
from ..agents.error_handler import ErrorHandler
from ..utils.logging_utils import setup_logging
import logging

# Set up logging for this module
setup_logging()
logger = logging.getLogger(__name__)

class PolicyReasoningAgent:
    """
    Agent to generate detailed reasoning for a classification decision using LLM.
    """
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=Config.DIAL_API_KEY,
            api_version=Config.DIAL_API_VERSION,
            azure_endpoint=Config.DIAL_ENDPOINT
        )
        self.error_handler = ErrorHandler()
    
    def generate_reasoning(self, text: str, classification: Dict, retrieved_docs: List[Dict]) -> Dict:
        """
        Generate a detailed explanation for the classification, referencing policies and context.
        """
        try:
            # Prepare context from retrieved documents
            context = self._prepare_context(retrieved_docs)
            
            prompt = f"""
            Based on the classification and relevant policies, provide a detailed explanation 
            for why this content was classified as "{classification['label']}".
            
            Original Text: "{text}"
            Classification: {classification['label']} (Confidence: {classification['confidence']})
            Initial Explanation: {classification['explanation']}
            
            Relevant Policies:
            {context}
            
            Provide a comprehensive reasoning that:
            1. References specific policy violations (if any)
            2. Explains the severity of the content
            3. Justifies the classification decision
            4. Mentions any contextual factors
            
            Keep the response professional and objective.
            """
            
            response = self.client.chat.completions.create(
                model=Config.DEPLOYMENT_NAME,
                temperature=0.2,
                messages=[
                    {"role": "system", "content": "You are a content moderation expert providing detailed policy analysis."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                "success": True,
                "reasoning": response.choices[0].message.content,
                "policies_referenced": len(retrieved_docs)
            }
            
        except Exception as e:
            # Handle errors gracefully
            return self.error_handler.handle_error(e, "PolicyReasoningAgent.generate_reasoning")
    
    def _prepare_context(self, documents: List[Dict]) -> str:
        """
        Prepare a string context from retrieved policy documents for the LLM prompt.
        """
        context = ""
        for i, doc in enumerate(documents, 1):
            context += f"\n{i}. From {doc['source']}:\n{doc['text']}\n"
        return context