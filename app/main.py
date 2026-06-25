from contextlib import asynccontextmanager
from typing import Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession

from app.config import get_settings

# Jinja2 templates — initialized at module level (no async needed)
templates = Jinja2Templates(directory="app/templates")

# Database globals — set during lifespan startup
_engine: AsyncEngine | None = None
_async_session: async_sessionmaker[AsyncSession] | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Application lifespan: init DB, seed data, cleanup."""
    global _engine, _async_session

    settings = get_settings()

    # Initialize database
    from app.models.base import init_db

    _engine, _async_session = await init_db(settings.database_url)

    # Seed initial data
    from app.services.seed_data import seed_templates

    await seed_templates(_async_session)

    yield

    # Cleanup
    if _engine:
        await _engine.dispose()


def create_app() -> FastAPI:
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="文生图应用 — 巨构与人的对比 (Megastructure vs Human Scale)",
        lifespan=lifespan,
    )

    # Mount static files
    import os

    os.makedirs("app/static/generated", exist_ok=True)
    os.makedirs("app/static/generated/thumbnails", exist_ok=True)

    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Register routers
    from app.routers import pages, generate, gallery, templates_api, collections_api

    app.include_router(pages.router)
    app.include_router(generate.router)
    app.include_router(gallery.router)
    app.include_router(templates_api.router)
    app.include_router(collections_api.router)

    return app


app = create_app()
