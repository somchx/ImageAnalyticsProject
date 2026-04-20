from fastapi import APIRouter
from app.api.endpoints import upload, sessions, metrics, events, settings, export, notifications

api_router = APIRouter()
api_router.include_router(upload.router, prefix="/upload", tags=["upload"])
api_router.include_router(sessions.router, prefix="/sessions", tags=["sessions"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(settings.router, prefix="/settings", tags=["settings"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
