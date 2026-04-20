import time
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.db.database import get_db
from app.models.db.settings_model import SettingsRow
from app.models.schemas.settings import ThresholdSettings

router = APIRouter()


def get_thresholds_from_db(db: DBSession) -> ThresholdSettings:
    rows = db.query(SettingsRow).all()
    data = {r.key: r.value for r in rows}

    def f(key, default):
        return float(data.get(key, default))

    def i(key, default):
        return int(data.get(key, default))

    def b(key, default):
        v = data.get(key, str(default)).lower()
        return v in ("true", "1", "yes")

    def s(key, default=""):
        return data.get(key, default)

    return ThresholdSettings(
        l_star_cooking_max=f("l_star_cooking_max", 65.0),
        l_star_ready_to_flip_max=f("l_star_ready_to_flip_max", 52.0),
        l_star_ready_max=f("l_star_ready_max", 42.0),
        l_star_overcooked_max=f("l_star_overcooked_max", 32.0),
        l_star_burnt_max=f("l_star_burnt_max", 22.0),
        browning_cooking_min=f("browning_cooking_min", 0.15),
        browning_ready_to_flip_min=f("browning_ready_to_flip_min", 0.40),
        browning_ready_min=f("browning_ready_min", 0.55),
        browning_overcooked_min=f("browning_overcooked_min", 0.72),
        browning_burnt_min=f("browning_burnt_min", 0.88),
        burn_risk_warning_pct=f("burn_risk_warning_pct", 10.0),
        burn_risk_critical_pct=f("burn_risk_critical_pct", 20.0),
        smoke_warning_threshold=f("smoke_warning_threshold", 0.30),
        smoke_critical_threshold=f("smoke_critical_threshold", 0.55),
        smoothing_window=i("smoothing_window", 7),
        alert_cooldown_seconds=f("alert_cooldown_seconds", 30.0),
        frame_sample_interval=i("frame_sample_interval", 1),
        telegram_enabled=b("telegram_enabled", False),
        telegram_bot_token=s("telegram_bot_token"),
        telegram_chat_id=s("telegram_chat_id"),
    )


@router.get("", response_model=ThresholdSettings)
def get_settings(db: DBSession = Depends(get_db)):
    return get_thresholds_from_db(db)


@router.put("", response_model=ThresholdSettings)
def update_settings(body: ThresholdSettings, db: DBSession = Depends(get_db)):
    now = int(time.time() * 1000)
    updates = body.model_dump()
    for key, value in updates.items():
        row = db.query(SettingsRow).filter(SettingsRow.key == key).first()
        if row:
            row.value = str(value)
            row.updated_at = now
        else:
            db.add(SettingsRow(key=key, value=str(value), updated_at=now))
    db.commit()
    return get_thresholds_from_db(db)
