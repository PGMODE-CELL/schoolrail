import os
import asyncio
import asyncpg
import bcrypt

DB_URL = os.environ.get("SHARED_DB_URL", "postgresql://schoolrail:password@localhost:5432/schoolrail")

SEED_TENANT_ID = "default"
SEED_USERS = [
    {
        "email": "admin@schoolrail.com",
        "password": "admin123",
        "full_name": "Admin User",
        "roles": ["admin", "superadmin"],
    },
    {
        "email": "driver1@schoolrail.com",
        "password": "admin123",
        "full_name": "Driver John",
        "roles": ["driver"],
    },
    {
        "email": "parent1@schoolrail.com",
        "password": "admin123",
        "full_name": "Parent Sarah",
        "roles": ["parent"],
    },
]

SEED_VEHICLES = [
    {"plate_number": "BUS-001", "make": "Blue Bird", "model": "Vision", "year": 2023, "capacity": 54},
    {"plate_number": "BUS-002", "make": "Thomas Built", "model": "Saf-T-Liner", "year": 2024, "capacity": 48},
    {"plate_number": "BUS-003", "make": "IC Bus", "model": "CE Series", "year": 2023, "capacity": 60},
]

async def seed():
    tenant_db = f"tenant_{SEED_TENANT_ID}"

    conn = await asyncpg.connect(DB_URL)
    exists = await conn.fetchval("SELECT 1 FROM pg_database WHERE datname = $1", tenant_db)
    if not exists:
        await conn.execute(f'CREATE DATABASE "{tenant_db}"')
    await conn.close()

    db_url = DB_URL.replace("schoolrail", tenant_db)
    conn = await asyncpg.connect(db_url)

    await conn.execute("CREATE SCHEMA IF NOT EXISTS schoolrail")
    await conn.execute("SET search_path TO schoolrail")

    with open("backend/services/tenant/schema.sql") as f:
        sql = f.read()
    await conn.execute(sql)

    for user in SEED_USERS:
        pw_hash = bcrypt.hashpw(user["password"].encode(), bcrypt.gensalt(12)).decode()
        await conn.execute(
            "INSERT INTO users (tenant_id, email, password_hash, full_name, roles) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (tenant_id, email) DO NOTHING",
            SEED_TENANT_ID, user["email"], pw_hash, user["full_name"], user["roles"],
        )

    for v in SEED_VEHICLES:
        await conn.execute(
            "INSERT INTO vehicles (tenant_id, plate_number, make, model, year, capacity) VALUES ($1, $2, $3, $4, $5, $6) ON CONFLICT DO NOTHING",
            SEED_TENANT_ID, v["plate_number"], v["make"], v["model"], v["year"], v["capacity"],
        )

    await conn.close()
    print(f"Seeded tenant '{SEED_TENANT_ID}' with default users and vehicles")
    print("Login: admin@schoolrail.com / admin123")

if __name__ == "__main__":
    asyncio.run(seed())
