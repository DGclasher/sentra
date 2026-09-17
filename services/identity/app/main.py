from fastapi import FastAPI
from app.api import routes

app = FastAPI(title="Identity Service")

app.include_router(routes.router, tags=["User profile"])


@app.get("/", tags=["Health"])
def root():
    return {"service": "identity-service", "version": "1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.get("/ready", tags=["Health"])
def readiness():
    return {"ready": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
