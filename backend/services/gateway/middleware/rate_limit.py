import time
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.services.gateway.main import rate_limiter

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_requests: int = 60, window_seconds: int = 60):
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def dispatch(self, request: Request, call_next):
        tenant_id = getattr(request.state, "tenant_id", "anonymous")
        client_ip = request.client.host if request.client else "unknown"
        key = f"ratelimit:{tenant_id}:{client_ip}:{request.url.path}"
        if rate_limiter:
            allowed, remaining = await rate_limiter.check(key, self.max_requests, self.window_seconds)
            if not allowed:
                retry_after = self.window_seconds
                raise HTTPException(
                    status_code=429,
                    detail={"code": "RATE_LIMITED", "message": "Too many requests"},
                    headers={"Retry-After": str(retry_after)},
                )
        response = await call_next(request)
        return response
