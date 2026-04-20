from pydantic import BaseModel
from typing import Optional


class EventOut(BaseModel):
    id: int
    session_id: str
    frame_index: int
    timestamp_ms: int
    event_type: str
    severity: Optional[str]
    event_code: str
    from_state: Optional[str]
    to_state: Optional[str]
    trigger_metric: Optional[str]
    trigger_value: Optional[float]
    message: str
    metric_snapshot: Optional[str]
    telegram_sent: int

    model_config = {"from_attributes": True}
