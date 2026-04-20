from pydantic import BaseModel
from typing import Optional


class ThresholdSettings(BaseModel):
    l_star_cooking_max: float = 65.0
    l_star_ready_to_flip_max: float = 52.0
    l_star_ready_max: float = 42.0
    l_star_overcooked_max: float = 32.0
    l_star_burnt_max: float = 22.0
    browning_cooking_min: float = 0.15
    browning_ready_to_flip_min: float = 0.40
    browning_ready_min: float = 0.55
    browning_overcooked_min: float = 0.72
    browning_burnt_min: float = 0.88
    burn_risk_warning_pct: float = 10.0
    burn_risk_critical_pct: float = 20.0
    smoke_warning_threshold: float = 0.30
    smoke_critical_threshold: float = 0.55
    smoothing_window: int = 7
    alert_cooldown_seconds: float = 30.0
    frame_sample_interval: int = 1
    telegram_enabled: bool = False
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
