from pydantic import BaseModel
from typing import Dict, List, Optional

class TextInput(BaseModel):
    """
    Schema for text input to the /analyze endpoint.
    """
    text: str
    include_policies: bool = True
    include_reasoning: bool = True

class AnalysisResponse(BaseModel):
    """
    Schema for the response from the /analyze endpoint.
    Includes classification, policies, reasoning, recommended action, and timestamp.
    """
    classification: Dict
    retrieved_policies: Optional[List[Dict]] = None
    reasoning: Optional[str] = None
    recommended_action: Optional[Dict] = None
    timestamp: str