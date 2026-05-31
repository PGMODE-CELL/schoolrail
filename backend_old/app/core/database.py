"""
SchoolRail Database Configuration
SQLAlchemy setup with async support
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from typing import Generator
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./schoolrail.db")

try:
    async_engine = create_async_engine(
        DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://").replace("sqlite:///", "sqlite+aiosqlite:///"),
        echo=False,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )
except Exception:
    DATABASE_URL = "sqlite:///./schoolrail.db"
    async_engine = create_async_engine(
        DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///"),
        echo=False
    )

sync_engine = create_engine(
    DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://").replace("sqlite+aiosqlite:///", "sqlite:///"),
    echo=False,
    pool_pre_ping=True
)

engine = sync_engine

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


async def get_async_db() -> Generator[AsyncSession, None, None]:
    """Get async database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_db() -> Generator[SessionLocal, None, None]:
    """Get sync database session"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def init_db():
    """Initialize database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """Drop all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)