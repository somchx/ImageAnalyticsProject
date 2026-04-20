from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import time

from app.config import settings
from app.models.db.base import Base
from app.models.db.session_model import Session  # noqa: F401
from app.models.db.frame_metric_model import FrameMetric  # noqa: F401
from app.models.db.event_model import Event  # noqa: F401
from app.models.db.settings_model import SettingsRow  # noqa: F401

Path("./data").mkdir(parents=True, exist_ok=True)
Path("./data/sessions").mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

DEFAULT_SETTINGS = {
    "l_star_cooking_max": "65.0",
    "l_star_ready_to_flip_max": "52.0",
    "l_star_ready_max": "42.0",
    "l_star_overcooked_max": "32.0",
    "l_star_burnt_max": "22.0",
    "browning_cooking_min": "0.15",
    "browning_ready_to_flip_min": "0.40",
    "browning_ready_min": "0.55",
    "browning_overcooked_min": "0.72",
    "browning_burnt_min": "0.88",
    "burn_risk_warning_pct": "10.0",
    "burn_risk_critical_pct": "20.0",
    "smoke_warning_threshold": "0.30",
    "smoke_critical_threshold": "0.55",
    "smoothing_window": "7",
    "alert_cooldown_seconds": "30",
    "frame_sample_interval": "1",
    "telegram_enabled": "false",
    "telegram_bot_token": "",
    "telegram_chat_id": "",
}


def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        now = int(time.time() * 1000)
        for key, value in DEFAULT_SETTINGS.items():
            existing = db.query(SettingsRow).filter(SettingsRow.key == key).first()
            if not existing:
                db.add(SettingsRow(key=key, value=value, updated_at=now))
        db.commit()
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
