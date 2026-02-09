"""
Database connection and session management.
Supports both PostgreSQL (production) and SQLite (development).
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from .config import settings


# Choose database URL based on configuration
if settings.USE_SQLITE:
    DATABASE_URL = settings.SQLITE_URL
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        connect_args={"check_same_thread": False}
    )
else:
    DATABASE_URL = settings.DATABASE_URL
    engine = create_async_engine(
        DATABASE_URL,
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""
    pass


async def get_db() -> AsyncSession:
    """
    Dependency for getting database sessions.
    Yields an async session and ensures proper cleanup.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections."""
    await engine.dispose()
