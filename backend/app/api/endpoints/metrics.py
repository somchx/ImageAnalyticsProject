from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from typing import List, Optional

from app.db.database import get_db
from app.models.db.frame_metric_model import FrameMetric
from app.models.schemas.metrics import FrameMetricsOut, MetricsSummary

router = APIRouter()


@router.get("/{session_id}", response_model=List[FrameMetricsOut])
def get_metrics(
    session_id: str,
    page: int = 0,
    limit: int = 500,
    db: DBSession = Depends(get_db),
):
    return (
        db.query(FrameMetric)
        .filter(FrameMetric.session_id == session_id)
        .order_by(FrameMetric.frame_index)
        .offset(page * limit)
        .limit(limit)
        .all()
    )


@router.get("/{session_id}/summary", response_model=MetricsSummary)
def get_summary(session_id: str, db: DBSession = Depends(get_db)):
    rows = db.query(FrameMetric).filter(FrameMetric.session_id == session_id).all()
    if not rows:
        raise HTTPException(status_code=404, detail="No metrics found for session")

    L_values = [r.L_star_mean for r in rows]
    browning = [r.browning_score for r in rows]
    burn_risk = [r.burn_risk_area_pct for r in rows]
    smoke = [r.smoke_density for r in rows]

    return MetricsSummary(
        session_id=session_id,
        total_frames=len(rows),
        avg_L_star=sum(L_values) / len(L_values),
        min_L_star=min(L_values),
        max_L_star=max(L_values),
        avg_browning=sum(browning) / len(browning),
        max_burn_risk_pct=max(burn_risk),
        avg_smoke_density=sum(smoke) / len(smoke),
        final_state=rows[-1].grill_state if rows else None,
    )
