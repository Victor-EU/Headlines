import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.admin import router as admin_auth_router
from app.config import settings
from app.routers import briefing, categories, events, feed, headlines
from app.routers import (
    admin_analytics,
    admin_articles,
    admin_categories,
    admin_models,
    admin_sources,
    admin_system,
    admin_tasks,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = None
    if settings.RUN_SCHEDULER:
        from app.workers.scheduler import start_scheduler

        scheduler = await start_scheduler()
        logger.info("Scheduler started in API process")
    yield
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler shut down")


app = FastAPI(title="Headlines API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(headlines.router)
app.include_router(categories.router)
app.include_router(briefing.router)
app.include_router(events.router)
app.include_router(feed.router)

app.include_router(admin_auth_router)
app.include_router(admin_sources.router)
app.include_router(admin_categories.router)
app.include_router(admin_models.router)
app.include_router(admin_tasks.router)
app.include_router(admin_articles.router)
app.include_router(admin_system.router)
app.include_router(admin_analytics.router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
