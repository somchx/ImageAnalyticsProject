from sqlalchemy import Column, String, Integer
from app.models.db.base import Base


class SettingsRow(Base):
    __tablename__ = "settings"

    key = Column(String, primary_key=True)
    value = Column(String, nullable=False)
    updated_at = Column(Integer, nullable=False, default=0)
