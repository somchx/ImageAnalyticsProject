from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, Index
from app.models.db.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    frame_index = Column(Integer, nullable=False)
    timestamp_ms = Column(Integer, nullable=False)
    event_type = Column(String, nullable=False)  # STATE_CHANGE | ALERT
    severity = Column(String, nullable=True)  # WARNING | CRITICAL
    event_code = Column(String, nullable=False)
    from_state = Column(String, nullable=True)
    to_state = Column(String, nullable=True)
    trigger_metric = Column(String, nullable=True)
    trigger_value = Column(Float, nullable=True)
    trigger_threshold = Column(Float, nullable=True)
    message = Column(Text, nullable=False)
    metric_snapshot = Column(Text, nullable=True)  # JSON blob
    telegram_sent = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_ev_session_ts", "session_id", "timestamp_ms"),
    )
