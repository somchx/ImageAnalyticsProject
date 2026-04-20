"""
Session lifecycle management.
Each session has its own smoother, state machine, and alert engine instances.
"""

import uuid
import json
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session as DBSession

from app.core.smoother import MovingAverageSmoother
from app.core.state_machine import GrillStateMachine
from app.core.alert_engine import AlertEngine
from app.models.db.session_model import Session as SessionModel
from app.models.schemas.settings import ThresholdSettings
from app.utils.time_utils import now_ms

# In-memory per-session processing context
_session_contexts: Dict[str, Dict[str, Any]] = {}


def create_session(
    db: DBSession,
    name: str,
    source_type: str,
    thresholds: ThresholdSettings,
    source_filename: Optional[str] = None,
) -> str:
    session_id = str(uuid.uuid4())
    now = now_ms()
    db_session = SessionModel(
        id=session_id,
        name=name or f"Session {session_id[:8]}",
        source_type=source_type,
        source_filename=source_filename,
        status="ACTIVE",
        created_at=now,
        settings_snapshot=json.dumps(thresholds.model_dump()),
    )
    db.add(db_session)
    db.commit()

    _session_contexts[session_id] = {
        "smoother": MovingAverageSmoother(window=thresholds.smoothing_window),
        "state_machine": GrillStateMachine(thresholds),
        "alert_engine": AlertEngine(cooldown_seconds=thresholds.alert_cooldown_seconds),
        "frame_counter": 0,
    }
    return session_id


def get_session_context(session_id: str) -> Optional[Dict[str, Any]]:
    return _session_contexts.get(session_id)


def increment_frame(session_id: str) -> int:
    ctx = _session_contexts.get(session_id)
    if ctx is None:
        return 0
    ctx["frame_counter"] += 1
    return ctx["frame_counter"] - 1


def close_session(db: DBSession, session_id: str, final_state: str):
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if db_session:
        db_session.status = "CLOSED"
        db_session.closed_at = now_ms()
        db_session.final_state = final_state
        db.commit()
    _session_contexts.pop(session_id, None)


def update_session_frame_count(db: DBSession, session_id: str, count: int):
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if db_session:
        db_session.total_frames = count
        db.commit()
