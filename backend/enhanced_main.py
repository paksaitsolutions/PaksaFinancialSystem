"""
Enhanced FastAPI application with more features from main.py
"""
import logging
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

# Setup basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="Paksa Financial System",
    description="Enhanced API for debugging",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Test database connection
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Paksa Financial System...")
    try:
        # Try to import and initialize database
        from app.modules.core.database import init_db
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

# Root endpoint
@app.get("/", status_code=status.HTTP_200_OK)
async def root():
    return {
        "message": "Welcome to Paksa Financial System API",
        "status": "operational",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {
        "status": "ok",
        "database": "connected"  # This would be dynamic in production
    }

# This allows running with: python enhanced_main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("enhanced_main:app", host="0.0.0.0", port=8000, reload=True)
