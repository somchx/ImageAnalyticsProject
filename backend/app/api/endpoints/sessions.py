from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List

from app.db.database import get_db
from app.models.db.session_model import Session as SessionModel
from app.models.schemas.session import SessionOut, SessionCreate
from app.models.schemas.settings import ThresholdSettings
from app.services.session_service import create_session, close_session
from app.api.endpoints.settings import get_thresholds_from_db

router = APIRouter()


@router.get("", response_model=List[SessionOut])
def list_sessions(db: DBSession = Depends(get_db)):
    return db.query(SessionModel).order_by(SessionModel.created_at.desc()).all()


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: str, db: DBSession = Depends(get_db)):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return s


@router.post("", response_model=SessionOut)
def create_new_session(body: SessionCreate, db: DBSession = Depends(get_db)):
    thresholds = get_thresholds_from_db(db)
    sid = create_session(db, name=body.name, source_type=body.source_type, thresholds=thresholds)
    return db.query(SessionModel).filter(SessionModel.id == sid).first()


@router.patch("/{session_id}/close", response_model=SessionOut)
def close_session_endpoint(session_id: str, db: DBSession = Depends(get_db)):
    s = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    close_session(db, session_id, s.final_state or "UNKNOWN")
    return db.query(SessionModel).filter(SessionModel.id == session_id).first()
