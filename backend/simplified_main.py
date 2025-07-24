"""
Simplified version of the main FastAPI application for debugging.
"""
import logging
from fastapi import FastAPI
import uvicorn

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Paksa Financial System - Simplified",
    description="Simplified version for debugging",
    version="1.0.0"
)

# Basic health check endpoint
@app.get("/")
async def root():
    return {"message": "Simplified Paksa Financial System is running"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    logger.info("Starting simplified FastAPI application...")
    uvicorn.run(
        "simplified_main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="debug"
    )
