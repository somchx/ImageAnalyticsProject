from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey, UniqueConstraint, Index
from app.models.db.base import Base


class FrameMetric(Base):
    __tablename__ = "frame_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    frame_index = Column(Integer, nullable=False)
    timestamp_ms = Column(Integer, nullable=False)
    source_type = Column(String, nullable=False)

    L_star_mean = Column(Float, nullable=False)
    L_star_std = Column(Float, nullable=False)
    a_star_mean = Column(Float, nullable=False)
    a_star_std = Column(Float, nullable=False)
    b_star_mean = Column(Float, nullable=False)
    b_star_std = Column(Float, nullable=False)

    browning_score = Column(Float, nullable=False)
    cooked_area_pct = Column(Float, nullable=False)
    burn_risk_area_pct = Column(Float, nullable=False)
    smoke_density = Column(Float, nullable=False)

    L_star_smooth = Column(Float, nullable=False)
    browning_smooth = Column(Float, nullable=False)
    cooked_area_smooth = Column(Float, nullable=False)
    burn_risk_smooth = Column(Float, nullable=False)
    smoke_smooth = Column(Float, nullable=False)

    grill_state = Column(String, nullable=False)
    state_changed = Column(Integer, nullable=False, default=0)
    alert_codes = Column(String, nullable=False, default="")
    processing_time_ms = Column(Float, nullable=False)
    explanation = Column(Text, nullable=False, default="")

    __table_args__ = (
        UniqueConstraint("session_id", "frame_index"),
        Index("idx_fm_session_ts", "session_id", "timestamp_ms"),
    )
