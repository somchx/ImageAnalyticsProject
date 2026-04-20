from pydantic import BaseModel
from typing import Optional, Any, Dict


class WsFrameSubmit(BaseModel):
    type: str  # FRAME_SUBMIT
    payload: Dict[str, Any]


class WsControl(BaseModel):
    type: str  # CONTROL
    payload: Dict[str, str]


class RawMetrics(BaseModel):
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


class SmoothedMetrics(BaseModel):
    L_star_smooth: float
    browning_smooth: float
    cooked_area_smooth: float
    burn_risk_smooth: float
    smoke_smooth: float


class WsFrameResult(BaseModel):
    type: str = "FRAME_RESULT"
    payload: Dict[str, Any]


class WsAlert(BaseModel):
    type: str = "ALERT"
    payload: Dict[str, Any]


class WsStateChange(BaseModel):
    type: str = "STATE_CHANGE"
    payload: Dict[str, Any]


class WsError(BaseModel):
    type: str = "ERROR"
    payload: Dict[str, Any]
