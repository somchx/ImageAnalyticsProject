from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from typing import List

from app.db.database import get_db
from app.models.db.event_model import Event
from app.models.schemas.events import EventOut

router = APIRouter()


@router.get("/{session_id}", response_model=List[EventOut])
def get_events(session_id: str, db: DBSession = Depends(get_db)):
    return (
        db.query(Event)
        .filter(Event.session_id == session_id)
        .order_by(Event.timestamp_ms)
        .all()
    )
