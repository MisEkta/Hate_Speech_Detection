from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
import uvicorn
from datetime import datetime
from .analysis_service import analyze_text_service  # Import the service function
from ..schemas.text_schema import TextInput, AnalysisResponse  # <-- Updated import
from ..utils.logging_utils import setup_logging
import logging
from fastapi import APIRouter

# Set up logging for this module
setup_logging()
logger = logging.getLogger(__name__)

# Create FastAPI app and router
app = FastAPI(title="Hate Speech Detection API", version="1.0.0")
router = APIRouter()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_text(input_data: TextInput):
    """
    Endpoint to analyze text for hate speech and policy violations.
    Calls the analysis service and returns the results.
    """
    logger.info("Received /analyze request")
    try:
        response_data = analyze_text_service(
            input_data.text,
            include_policies=input_data.include_policies,
            include_reasoning=input_data.include_reasoning
        )
        logger.info("Analysis completed successfully")
        return AnalysisResponse(**response_data)
    except Exception as e:
        logger.error(f"Error in /analyze endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """
    Health check endpoint to verify API is running.
    """
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# Register router with the app
app.include_router(router)

if __name__ == "__main__":
    logger.info("Starting FastAPI server...")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")