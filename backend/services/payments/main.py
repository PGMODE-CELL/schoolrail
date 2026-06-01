from contextlib import asynccontextmanager
from fastapi import FastAPI
from prometheus_client import make_asgi_app

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(title="SchoolRail Payment Service", version="1.0.0", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "ok", "service": "payment-service", "version": "1.0.0"}

@app.get("/fees")
async def list_fees():
    return {"items": [], "total": 0}

@app.post("/fees")
async def create_fee():
    return {"status": "created", "id": "00000000-0000-0000-0000-000000000000"}

@app.get("/fees/{fee_id}")
async def get_fee(fee_id: str):
    return {"id": fee_id, "amount": 0, "status": "pending"}

@app.post("/fees/{fee_id}/pay")
async def pay_fee(fee_id: str):
    return {"status": "paid", "id": fee_id}

@app.get("/payments")
async def list_payments():
    return {"items": [], "total": 0}

@app.post("/payments")
async def create_payment():
    return {"status": "created", "id": "00000000-0000-0000-0000-000000000000"}
