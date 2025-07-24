"""
Test FastAPI startup with simplified database configuration.
"""
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(title="Paksa Financial System", version="0.1.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# Database test endpoint
@app.get("/db-test")
async def db_test():
    try:
        # Import here to avoid circular imports
        from app.core.db.session import engine
        from sqlalchemy import text
        
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            return {"status": "ok", "db_connection": "success", "result": result.scalar()}
    except Exception as e:
        return {"status": "error", "db_connection": "failed", "error": str(e)}

if __name__ == "__main__":
    print("Starting FastAPI server...")
    print(f"Test endpoint: http://127.0.0.1:8000/health")
    print(f"DB test endpoint: http://127.0.0.1:8000/db-test")
    uvicorn.run("test_fastapi_startup:app", host="0.0.0.0", port=8000, reload=True)
