from fastapi import FastAPI

from app.api.routes.staff_tickets import router as staff_tickets_router
from app.api.routes.user_tickets import router as user_tickets_router


app = FastAPI(title="Ticket Service")
app.include_router(user_tickets_router)
app.include_router(staff_tickets_router)


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}


@app.get("/ready", tags=["Health"])
def readiness():
    return {"ready": True}
