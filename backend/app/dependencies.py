from app.db.database import SessionLocal
from app.config import settings as app_settings


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_app_settings():
    return app_settings
