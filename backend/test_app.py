"""
Test FastAPI application to verify basic functionality.
"""
from fastapi import FastAPI

app = FastAPI(title="Test App")

@app.get("/")
async def read_root():
    return {"message": "Hello, Paksa Financial System!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test_app:app", host="0.0.0.0", port=8000, reload=True)
