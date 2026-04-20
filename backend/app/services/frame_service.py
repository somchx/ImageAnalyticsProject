"""
Converts a FrameResult into DB row and CSV row, persists both.
"""

from typing import Dict, Any
from sqlalchemy.orm import Session as DBSession

from app.core.pipeline import FrameResult
from app.models.db.frame_metric_model import FrameMetric
from app.models.db.event_model import Event
from app.utils.time_utils import now_ms


def build_metric_row(
    session_id: str,
    frame_index: int,
    timestamp_ms: int,
    source_type: str,
    result: FrameResult,
) -> Dict[str, Any]:
    alert_codes = "|".join(a.code for a in result.alerts) if result.alerts else ""
    return {
        "session_id": session_id,
        "frame_index": frame_index,
        "timestamp_ms": timestamp_ms,
        "source_type": source_type,
        "L_star_mean": result.raw_metrics.L_star_mean,
        "L_star_std": result.raw_metrics.L_star_std,
        "a_star_mean": result.raw_metrics.a_star_mean,
        "a_star_std": result.raw_metrics.a_star_std,
        "b_star_mean": result.raw_metrics.b_star_mean,
        "b_star_std": result.raw_metrics.b_star_std,
        "browning_score": result.raw_metrics.browning_score,
        "cooked_area_pct": result.raw_metrics.cooked_area_pct,
        "burn_risk_area_pct": result.raw_metrics.burn_risk_area_pct,
        "smoke_density": result.raw_metrics.smoke_density,
        "L_star_smooth": result.smoothed.get("L_star_smooth", result.raw_metrics.L_star_mean),
        "browning_smooth": result.smoothed.get("browning_smooth", result.raw_metrics.browning_score),
        "cooked_area_smooth": result.smoothed.get("cooked_area_smooth", result.raw_metrics.cooked_area_pct),
        "burn_risk_smooth": result.smoothed.get("burn_risk_smooth", result.raw_metrics.burn_risk_area_pct),
        "smoke_smooth": result.smoothed.get("smoke_smooth", result.raw_metrics.smoke_density),
        "grill_state": result.grill_state,
        "state_changed": 1 if result.state_changed else 0,
        "alert_codes": alert_codes,
        "processing_time_ms": result.processing_time_ms,
        "explanation": result.explanation,
    }


def store_frame_to_db(db: DBSession, row: Dict[str, Any]):
    metric = FrameMetric(**{k: v for k, v in row.items()})
    db.add(metric)


def store_events_to_db(
    db: DBSession,
    session_id: str,
    frame_index: int,
    result: FrameResult,
    telegram_sent_codes: set,
):
    if result.state_changed:
        event = Event(
            session_id=session_id,
            frame_index=frame_index,
            timestamp_ms=now_ms(),
            event_type="STATE_CHANGE",
            event_code=f"{result.prev_state}_TO_{result.grill_state}",
            from_state=result.prev_state,
            to_state=result.grill_state,
            message=f"State changed: {result.prev_state} → {result.grill_state}",
        )
        db.add(event)

    for alert in result.alerts:
        event = Event(
            session_id=session_id,
            frame_index=frame_index,
            timestamp_ms=now_ms(),
            event_type="ALERT",
            severity=alert.severity,
            event_code=alert.code,
            trigger_metric=alert.trigger_metric,
            trigger_value=alert.trigger_value,
            trigger_threshold=alert.trigger_threshold,
            message=alert.message,
            telegram_sent=1 if alert.code in telegram_sent_codes else 0,
        )
        db.add(event)
