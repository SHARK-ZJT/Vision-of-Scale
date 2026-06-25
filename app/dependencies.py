from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import get_settings


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    settings = get_settings()

    # Import here to avoid circular imports
    from app.main import _async_session

    async with _async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
