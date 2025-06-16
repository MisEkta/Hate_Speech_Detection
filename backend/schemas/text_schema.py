from pydantic import BaseModel
from typing import Dict, List, Optional

class TextInput(BaseModel):
    text: str
    include_policies: bool = True
    include_reasoning: bool = True

class AnalysisResponse(BaseModel):
    classification: Dict
    retrieved_policies: Optional[List[Dict]] = None
    reasoning: Optional[str] = None
    recommended_action: Optional[Dict] = None
    timestamp: str