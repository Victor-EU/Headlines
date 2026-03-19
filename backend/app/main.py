from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.admin import router as admin_auth_router
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Headlines API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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
