"""
Minimal FastAPI application to test basic functionality.
"""
from fastapi import FastAPI
import uvicorn
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Minimal Test App")

@app.get("/")
async def root():
    return {"message": "Hello from minimal FastAPI app!"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    logger.info("Starting minimal FastAPI app...")
    uvicorn.run("minimal_app:app", host="127.0.0.1", port=8000, reload=True)
