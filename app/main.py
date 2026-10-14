from fastapi import FastAPI

app = FastAPI(
    title="AI GitHub Engineering Assistant",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok"}