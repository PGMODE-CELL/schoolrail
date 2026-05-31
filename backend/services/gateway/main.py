import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app
from redis.asyncio import Redis

from backend.libs.shared.middleware import register_middlewares
from backend.libs.shared.security import JWTManager, RateLimiter
from backend.services.gateway.routes import router as gateway_router

logger = logging.getLogger("schoolrail.gateway")

redis: Redis = None
jwt_manager: JWTManager = None
rate_limiter: RateLimiter = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis, jwt_manager, rate_limiter
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    jwt_manager = JWTManager(
        public_keys={"default": open("/etc/keys/public.pem").read()},
        private_key=None,
    )
    rate_limiter = RateLimiter(redis)
    yield
    await redis.close()

app = FastAPI(title="SchoolRail API Gateway", version="1.0.0", lifespan=lifespan)

register_middlewares(app)

app.include_router(gateway_router)
app.mount("/metrics", make_asgi_app())

@app.get("/health")
async def health():
    return {"status": "ok", "service": "gateway", "version": "1.0.0"}

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error("unhandled_error", extra={
        "path": request.url.path,
        "method": request.method,
        "error": str(exc),
    })
    return JSONResponse(status_code=500, content={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"})
