import uuid
import shutil
import asyncio
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks
from sqlalchemy.orm import Session as DBSession

from app.db.database import get_db, SessionLocal
from app.utils.image_utils import bytes_to_bgr
from app.core.pipeline import run_pipeline
from app.core.smoother import MovingAverageSmoother
from app.core.state_machine import GrillStateMachine
from app.core.alert_engine import AlertEngine
from app.services.session_service import create_session
from app.services.frame_service import build_metric_row, store_frame_to_db, store_events_to_db
from app.utils.csv_writer import append_row_to_csv
from app.utils.time_utils import now_ms
from app.api.endpoints.settings import get_thresholds_from_db
from app.tasks.video_processor import process_video_file

router = APIRouter()

UPLOAD_DIR = Path("/tmp/grill_uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/image")
async def upload_image(
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    data = await file.read()
    bgr = bytes_to_bgr(data)
    if bgr is None:
        return {"error": "Could not decode image"}

    thresholds = get_thresholds_from_db(db)
    session_id = create_session(
        db, name=file.filename or "image", source_type="IMAGE",
        thresholds=thresholds, source_filename=file.filename
    )

    smoother = MovingAverageSmoother(window=thresholds.smoothing_window)
    sm = GrillStateMachine(thresholds)
    ae = AlertEngine(cooldown_seconds=thresholds.alert_cooldown_seconds)

    result = run_pipeline(bgr, smoother, sm, ae)
    ts = now_ms()

    row = build_metric_row(
        session_id=session_id, frame_index=0,
        timestamp_ms=ts, source_type="IMAGE", result=result
    )
    append_row_to_csv(session_id, row)
    store_frame_to_db(db, row)
    store_events_to_db(db, session_id, 0, result, set())
    db.commit()

    return {
        "session_id": session_id,
        "grill_state": result.grill_state,
        "explanation": result.explanation,
        "raw_metrics": {
            "L_star_mean": result.raw_metrics.L_star_mean,
            "a_star_mean": result.raw_metrics.a_star_mean,
            "b_star_mean": result.raw_metrics.b_star_mean,
            "browning_score": result.raw_metrics.browning_score,
            "cooked_area_pct": result.raw_metrics.cooked_area_pct,
            "burn_risk_area_pct": result.raw_metrics.burn_risk_area_pct,
            "smoke_density": result.raw_metrics.smoke_density,
        },
        "annotated_frame_b64": result.annotated_frame_b64,
        "dehazed_frame_b64": result.dehazed_frame_b64,
        "alerts": [{"code": a.code, "severity": a.severity, "message": a.message}
                   for a in result.alerts],
    }


@router.post("/video")
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: DBSession = Depends(get_db),
):
    thresholds = get_thresholds_from_db(db)
    session_id = create_session(
        db, name=file.filename or "video", source_type="VIDEO",
        thresholds=thresholds, source_filename=file.filename
    )

    tmp_path = UPLOAD_DIR / f"{session_id}_{file.filename}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    background_tasks.add_task(
        process_video_file,
        video_path=str(tmp_path),
        session_id=session_id,
        source_type="VIDEO",
        db_factory=SessionLocal,
        thresholds=thresholds,
    )

    return {"session_id": session_id, "status": "processing", "message": "Video is being processed."}
