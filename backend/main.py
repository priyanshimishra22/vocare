from fastapi import FastAPI

app = FastAPI(title="VocaCare API")


@app.get("/")
async def root():
    return {
        "message": "VocaCare API is running"
    }