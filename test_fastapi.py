from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Hello, World!"}

if __name__ == "__main__":
    print("Starting FastAPI server on http://localhost:8000")
    uvicorn.run("test_fastapi:app", host="0.0.0.0", port=8000, reload=True)
