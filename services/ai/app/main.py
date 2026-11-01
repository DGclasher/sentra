import logging
import os
import sys
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import admin_route, ai_route
from app.core.ticket_service_client import TicketServiceClient


logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ticket_client = ai_route.ai_service.llm_gateway.ticket_service_client
    http_client = httpx.AsyncClient(
        timeout=TicketServiceClient.DEFAULT_TIMEOUT,
    )
    ticket_client.set_client(http_client)
    try:
        yield
    finally:
        ticket_client.clear_client()
        await http_client.aclose()


app = FastAPI(title="AI Service", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

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
