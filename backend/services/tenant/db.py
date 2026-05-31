import asyncpg
from backend.libs.shared.models import TenantContext

SHARED_DB_URL = "postgresql://schoolrail:schoolrail@localhost:5432/schoolrail"

async def create_tenant_database(tenant_id: str, rotate: bool = False) -> str:
    conn = await asyncpg.connect(SHARED_DB_URL)
    try:
        db_name = f"tenant_{tenant_id}"
        exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", db_name)
        if not exists:
            await conn.execute(f'CREATE DATABASE "{db_name}"')
        db_url = f"postgresql+asyncpg://schoolrail:schoolrail@localhost:5432/{db_name}"
        return db_url
    finally:
        await conn.close()

async def run_tenant_migrations(tenant_id: str) -> None:
    db_name = f"tenant_{tenant_id}"
    conn = await asyncpg.connect(f"postgresql://schoolrail:schoolrail@localhost:5432/{db_name}")
    try:
        await conn.execute("CREATE SCHEMA IF NOT EXISTS schoolrail")
        await conn.execute("SET search_path TO schoolrail")
        with open("backend/services/tenant/schema.sql") as f:
            sql = f.read()
        await conn.execute(sql)
    finally:
        await conn.close()

async def drop_tenant_database(tenant_id: str) -> None:
    conn = await asyncpg.connect(SHARED_DB_URL)
    try:
        db_name = f"tenant_{tenant_id}"
        await conn.execute(f'DROP DATABASE IF EXISTS "{db_name}"')
    finally:
        await conn.close()

async def get_tenant_connection_string(tenant_id: str) -> TenantContext:
    db_name = f"tenant_{tenant_id}"
    return TenantContext(
        tenant_id=tenant_id,
        db_url=f"postgresql+asyncpg://schoolrail:schoolrail@localhost:5432/{db_name}",
        schema_name="schoolrail",
    )
