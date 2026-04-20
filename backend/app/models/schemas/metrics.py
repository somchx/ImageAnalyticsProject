from pydantic import BaseModel
from typing import Optional


class FrameMetricsOut(BaseModel):
    id: int
    session_id: str
    frame_index: int
    timestamp_ms: int
    source_type: str
    L_star_mean: float
    L_star_std: float
    a_star_mean: float
    a_star_std: float
    b_star_mean: float
    b_star_std: float
    browning_score: float
    cooked_area_pct: float
    burn_risk_area_pct: float
    smoke_density: float
    L_star_smooth: float
    browning_smooth: float
    cooked_area_smooth: float
    burn_risk_smooth: float
    smoke_smooth: float
    grill_state: str
    state_changed: int
    alert_codes: str
    processing_time_ms: float
    explanation: str

    model_config = {"from_attributes": True}


class MetricsSummary(BaseModel):
    session_id: str
    total_frames: int
    avg_L_star: float
    min_L_star: float
    max_L_star: float
    avg_browning: float
    max_burn_risk_pct: float
    avg_smoke_density: float
    final_state: Optional[str]
