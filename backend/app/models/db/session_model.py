from sqlalchemy import Column, String, Integer, Text
from app.models.db.base import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, default="")
    source_type = Column(String, nullable=False)  # IMAGE | VIDEO | WEBCAM
    source_filename = Column(String, nullable=True)
    status = Column(String, nullable=False, default="ACTIVE")  # ACTIVE | CLOSED | ERROR
    created_at = Column(Integer, nullable=False)
    closed_at = Column(Integer, nullable=True)
    total_frames = Column(Integer, nullable=False, default=0)
    final_state = Column(String, nullable=True)
    settings_snapshot = Column(Text, nullable=True)  # JSON blob
