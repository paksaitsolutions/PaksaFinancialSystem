from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import API router
from app.api.v1.api import api_router

app = FastAPI(
    title="Paksa Financial System",
    description="Financial Management System",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3003", "http://127.0.0.1:3003"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Paksa Financial System API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)