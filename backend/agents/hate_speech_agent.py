from openai import AzureOpenAI
from typing import Dict, Tuple
from backend.config import Config
from ..agents.error_handler import ErrorHandler
import json
import logging
import traceback
import re
from ..utils.logging_utils import setup_logging
import logging

# Set up logging for this module
setup_logging()
logger = logging.getLogger(__name__)

class HateSpeechDetectionAgent:
    """
    Agent for classifying text as Hate, Toxic, Offensive, Neutral, or Ambiguous using Azure OpenAI.
    """
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=Config.DIAL_API_KEY,
            api_version=Config.DIAL_API_VERSION,
            azure_endpoint=Config.DIAL_ENDPOINT
        )
        self.error_handler = ErrorHandler()
    
    def classify_text(self, text: str) -> dict:
        """
        Classify text and return label, confidence, and explanation.
        Uses a prompt to instruct the LLM to return a JSON response.
        """
        try:
            prompt = f"""
            Analyze the following text and classify it into one of these categories:
            - Hate: Contains hate speech targeting individuals or groups
            - Toxic: Harmful, abusive, or threatening language
            - Offensive: Inappropriate but not necessarily harmful
            - Neutral: Acceptable content
            - Ambiguous: Unclear or context-dependent
            
            Text to analyze: "{text}"
            
            Respond in JSON format:
            {{
                "label": "classification",
                "confidence": 0.95,
                "explanation": "Brief explanation of the classification"
            }}
            """
            
            response = self.client.chat.completions.create(
                model=Config.DEPLOYMENT_NAME,
                temperature=0.1,
                messages=[
                    {"role": "system", "content": "You are a content moderation expert."},
                    {"role": "user", "content": prompt}
                ]
            )
            print (f"Response from API: {response}")
            if not response.choices or not response.choices[0].message.content:
                return {
                    "success": False,
                    "message": "Empty response received from API"
                }
                
            content = response.choices[0].message.content

            # Clean Markdown formatting if present
            if isinstance(content, str):
                content = re.sub(r"^```[a-zA-Z]*\s*", "", content.strip())
                content = re.sub(r"\s*```$", "", content.strip())

            content = content.strip()
            if not content.startswith('{'):
                return {
                    "success": False,
                    "message": f"Invalid JSON response: {content}"
                }
                
            result = json.loads(content)
            # Ensure required keys exist
            return {
                "success": True,
                "label": result.get("label", "Ambiguous"),
                "confidence": result.get("confidence", 0.0),
                "explanation": result.get("explanation", "")
            }
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse JSON response: {str(e)}")
            return {
                "success": False,
                "message": "Invalid response format",
                "details": str(e)
            }
        except Exception as e:
            logging.error(f"Error in HateSpeechDetectionAgent.classify_text: {str(e)}")
            logging.error(f"Traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": "Classification failed",
                "details": str(e)
            }