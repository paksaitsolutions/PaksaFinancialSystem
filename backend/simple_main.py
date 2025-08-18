"""
Simple FastAPI application for debugging purposes.
"""
from fastapi import FastAPI

# Create FastAPI application
app = FastAPI(
    title="Paksa Financial System",
    description="Simple API for debugging",
    version="1.0.0"
)

@app.get("/")
async def root():
    return {"message": "Paksa Financial System API is running"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}

# This allows running with: python simple_main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("simple_main:app", host="0.0.0.0", port=8000, reload=True)
