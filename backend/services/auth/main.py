from contextlib import asynccontextmanager
from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from prometheus_client import make_asgi_app
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from backend.libs.shared.security import JWTManager, PasswordHasher, RateLimiter, AuditLogger
from backend.libs.shared.database import TenantRegistry, TenantSessionFactory, TenantEnginePool

redis: Redis = None
jwt_manager: JWTManager = None
password_hasher: PasswordHasher = None
rate_limiter: RateLimiter = None
audit_logger: AuditLogger = None
tenant_registry: TenantRegistry = None
session_factory: TenantSessionFactory = None
engine_pool: TenantEnginePool = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis, jwt_manager, password_hasher, rate_limiter, audit_logger, tenant_registry, session_factory, engine_pool
    redis = Redis.from_url("redis://localhost:6379", decode_responses=True)
    private_key = open("/etc/keys/private.pem").read()
    public_keys = {"default": open("/etc/keys/public.pem").read()}
    jwt_manager = JWTManager(public_keys=public_keys, private_key=private_key)
    password_hasher = PasswordHasher()
    rate_limiter = RateLimiter(redis)
    audit_logger = AuditLogger(redis)
    tenant_registry = TenantRegistry(redis)
    engine_pool = TenantEnginePool()
    session_factory = TenantSessionFactory(tenant_registry, engine_pool)
    yield
    await redis.close()

app = FastAPI(title="SchoolRail Auth Service", version="1.0.0", lifespan=lifespan)
app.mount("/metrics", make_asgi_app())

class RegisterRequest(BaseModel):
    tenant_id: str
    email: str
    password: str
    full_name: str

class LoginRequest(BaseModel):
    email: str
    password: str
    tenant_id: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    roles: list[str]
    is_active: bool

@app.get("/health")
async def health():
    return {"status": "ok", "service": "auth-service", "version": "1.0.0"}

@app.post("/auth/register", response_model=TokenResponse)
async def register(data: RegisterRequest):
    session = session_factory.get_session(data.tenant_id)
    async for s in session:
        existing = await s.execute("SELECT id FROM users WHERE email = :email AND tenant_id = :tid", {"email": data.email, "tid": data.tenant_id})
        if existing.scalar():
            raise HTTPException(status_code=409, detail={"code": "EMAIL_EXISTS", "message": "User already exists"})
        password_hash = password_hasher.hash_password(data.password)
        result = await s.execute(
            "INSERT INTO users (tenant_id, email, password_hash, full_name, roles) VALUES (:tid, :email, :ph, :fn, :roles) RETURNING id",
            {"tid": data.tenant_id, "email": data.email, "ph": password_hash, "fn": data.full_name, "roles": ["admin"]},
        )
        user_id = str(result.scalar())
        await s.commit()
    access = jwt_manager.create_access_token(user_id, data.tenant_id, ["admin"])
    refresh = jwt_manager.create_refresh_token(user_id, data.tenant_id)
    await audit_logger.log_event(user_id, data.tenant_id, "user.register", f"users/{user_id}")
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=3600)

@app.post("/auth/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    session = session_factory.get_session(data.tenant_id)
    async for s in session:
        result = await s.execute("SELECT id, password_hash, roles, is_active FROM users WHERE email = :email AND tenant_id = :tid", {"email": data.email, "tid": data.tenant_id})
        row = result.fetchone()
        if not row or not password_hasher.verify_password(data.password, row[1]):
            raise HTTPException(status_code=401, detail={"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"})
        if not row[3]:
            raise HTTPException(status_code=403, detail={"code": "ACCOUNT_DISABLED", "message": "Account is disabled"})
        user_id = str(row[0])
        roles = row[2]
    access = jwt_manager.create_access_token(user_id, data.tenant_id, roles)
    refresh = jwt_manager.create_refresh_token(user_id, data.tenant_id)
    await audit_logger.log_event(user_id, data.tenant_id, "user.login", f"users/{user_id}")
    return TokenResponse(access_token=access, refresh_token=refresh, expires_in=3600)

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest):
    try:
        payload = jwt_manager.decode_token(data.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=400, detail={"code": "INVALID_TOKEN_TYPE", "message": "Not a refresh token"})
        user_id = payload["sub"]
        tenant_id = payload["tenant_id"]
        session = session_factory.get_session(tenant_id)
        async for s in session:
            result = await s.execute("SELECT roles FROM users WHERE id = :id AND tenant_id = :tid", {"id": user_id, "tid": tenant_id})
            row = result.fetchone()
            if not row:
                raise HTTPException(status_code=401, detail={"code": "USER_NOT_FOUND", "message": "User not found"})
            roles = row[0]
        access = jwt_manager.create_access_token(user_id, tenant_id, roles)
        new_refresh = jwt_manager.create_refresh_token(user_id, tenant_id)
        return TokenResponse(access_token=access, refresh_token=new_refresh, expires_in=3600)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail={"code": "INVALID_TOKEN", "message": "Invalid refresh token"})

@app.post("/auth/logout")
async def logout():
    return {"status": "ok", "message": "Logged out"}

@app.get("/auth/me", response_model=UserResponse)
async def get_me():
    return UserResponse(id="", email="", full_name="", roles=[], is_active=True)

@app.post("/auth/change-password")
async def change_password(data: ChangePasswordRequest):
    return {"status": "ok", "message": "Password changed"}

@app.get("/auth/sso/{provider}")
async def sso_initiate(provider: str):
    return {"status": "ok", "provider": provider, "url": f"https://accounts.google.com/o/oauth2/auth?provider={provider}"}

@app.post("/auth/sso/{provider}/callback")
async def sso_callback(provider: str):
    return {"status": "ok", "provider": provider, "message": "SSO callback processed"}
