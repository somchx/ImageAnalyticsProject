"""
Background task for processing uploaded video files frame-by-frame.
Samples at the configured interval, writes metrics to DB+CSV, and
broadcasts results via WebSocket.
"""

import asyncio
import cv2
import time
from pathlib import Path
from sqlalchemy.orm import Session as DBSession

from app.core.pipeline import run_pipeline
from app.services.session_service import get_session_context
from app.services.frame_service import build_metric_row, store_frame_to_db
from app.services.websocket_manager import manager
from app.utils.csv_writer import append_row_to_csv
from app.utils.time_utils import now_ms
from app.models.schemas.settings import ThresholdSettings


async def process_video_file(
    video_path: str,
    session_id: str,
    source_type: str,
    db_factory,
    thresholds: ThresholdSettings,
):
    """
    Opens the video file, samples frames at `thresholds.frame_sample_interval`,
    runs the pipeline on each, stores results, and broadcasts over WebSocket.
    Runs in a background thread (called via asyncio.to_thread or BackgroundTask).
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        await manager.broadcast(session_id, {
            "type": "ERROR",
            "payload": {"code": "VIDEO_OPEN_FAILED", "message": f"Cannot open {video_path}"}
        })
        return

    ctx = get_session_context(session_id)
    if ctx is None:
        return

    smoother = ctx["smoother"]
    state_machine = ctx["state_machine"]
    alert_engine = ctx["alert_engine"]

    frame_index = 0
    sample_interval = max(1, thresholds.frame_sample_interval)

    try:
        while True:
            ret, bgr_frame = cap.read()
            if not ret:
                break

            if frame_index % sample_interval != 0:
                frame_index += 1
                continue

            result = run_pipeline(bgr_frame, smoother, state_machine, alert_engine)
            ts = now_ms()

            row = build_metric_row(
                session_id=session_id,
                frame_index=frame_index,
                timestamp_ms=ts,
                source_type=source_type,
                result=result,
            )
            append_row_to_csv(session_id, row)

            db = db_factory()
            try:
                store_frame_to_db(db, row)
                db.commit()
            finally:
                db.close()

            ws_payload = _build_ws_frame_result(session_id, frame_index, ts, result)
            await manager.broadcast(session_id, ws_payload)

            # Small sleep to avoid blocking the event loop entirely
            await asyncio.sleep(0)
            frame_index += 1

    finally:
        cap.release()
        try:
            Path(video_path).unlink(missing_ok=True)
        except Exception:
            pass

    # Signal completion
    await manager.broadcast(session_id, {
        "type": "VIDEO_COMPLETE",
        "payload": {"session_id": session_id, "total_frames": frame_index}
    })


def _build_ws_frame_result(session_id, frame_index, ts, result) -> dict:
    return {
        "type": "FRAME_RESULT",
        "payload": {
            "session_id": session_id,
            "frame_index": frame_index,
            "timestamp_ms": ts,
            "raw_metrics": {
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
            },
            "smoothed_metrics": result.smoothed,
            "grill_state": result.grill_state,
            "prev_state": result.prev_state,
            "state_changed": result.state_changed,
            "annotated_frame_b64": result.annotated_frame_b64,
            "dehazed_frame_b64": result.dehazed_frame_b64,
            "roi_mask_b64": result.roi_mask_b64,
            "explanation": result.explanation,
            "processing_time_ms": result.processing_time_ms,
            "alerts": [
                {"code": a.code, "severity": a.severity, "message": a.message}
                for a in result.alerts
            ],
        }
    }
