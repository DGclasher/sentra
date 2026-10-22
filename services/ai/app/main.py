from fastapi import FastAPI
from app.api.routes import admin_route, ai_route

app = FastAPI(title="AI Service")

app.include_router(admin_route.router, tags=["Admin"])
app.include_router(ai_route.router, tags=["AI"])


@app.get("/", tags=["Health"])
def root():
    return {"service": "ai-service", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.get("/ready", tags=["Health"])
def readiness():
    return {"ready": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
