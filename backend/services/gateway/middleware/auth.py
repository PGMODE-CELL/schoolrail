from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from backend.services.gateway.main import jwt_manager
from backend.services.gateway.routes import ROUTE_TABLE, RouteConfig
import re

class JWTAuthMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        if path in ("/health", "/metrics"):
            return await call_next(request)
        config = self._match_config(path)
        if config and config["auth_required"]:
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                raise HTTPException(status_code=401, detail={"code": "MISSING_TOKEN", "message": "Authorization header required"})
            token = auth_header.split(" ")[1]
            try:
                payload = jwt_manager.decode_token(token)
                request.state.user_id = payload.get("sub")
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user_roles = payload.get("roles", [])
                if config.get("scopes"):
                    user_scopes = set(payload.get("roles", []))
                    required_scopes = set(config["scopes"])
                    if not user_scopes.intersection(required_scopes):
                        raise HTTPException(status_code=403, detail={"code": "FORBIDDEN", "message": "Insufficient permissions"})
            except HTTPException:
                raise
            except Exception:
                raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Token is invalid or expired"})
        response = await call_next(request)
        return response

    def _match_config(self, path: str) -> RouteConfig:
        for prefix, config in sorted(ROUTE_TABLE.items(), key=lambda x: -len(x[0])):
            if path.startswith(prefix):
                return config
        return None
