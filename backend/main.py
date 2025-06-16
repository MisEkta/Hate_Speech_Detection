from .utils.logging_utils import setup_logging
import logging
import uvicorn
from .api.api_main import analyze_text, health_check  # Import the endpoints
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.api_main import router as analyze_router  # <-- Import the router

# Initialize logging
setup_logging()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hate Speech Detection API",
    description="API for hate speech detection and policy retrieval",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analyze_router)  # <-- Use the router, not the function

@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint for health check and API information.
    """
    return {
        "status": "online",
        "api_name": "Hate Speech Detection API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze",
            "health": "/health"
            # Add more as you modularize
        }
    }

if __name__ == "__main__":
    logger.info("Starting FastAPI server from main.py...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )