from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    database_url: str = "sqlite:///./data/grill_analytics.db"
    data_dir: str = "./data/sessions"
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    telegram_enabled: bool = False
    alert_cooldown_seconds: float = 30.0
    smoothing_window: int = 7
    frame_sample_interval: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
