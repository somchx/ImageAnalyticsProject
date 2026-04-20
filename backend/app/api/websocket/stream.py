"""
WebSocket endpoint for real-time frame processing.
Client sends base64-encoded JPEG frames; server returns processed results.
"""

import json
import base64
import asyncio
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.db.database import SessionLocal
from app.services.websocket_manager import manager
from app.services.session_service import (
    create_session, get_session_context, increment_frame, close_session
)
from app.services.frame_service import build_metric_row, store_frame_to_db, store_events_to_db
from app.services.telegram_service import send_telegram_alert
from app.utils.image_utils import decode_b64_to_bgr
from app.utils.csv_writer import append_row_to_csv
from app.utils.time_utils import now_ms
from app.core.pipeline import run_pipeline
from app.api.endpoints.settings import get_thresholds_from_db

logger = logging.getLogger(__name__)
ws_router = APIRouter()


@ws_router.websocket("/ws/stream/{session_id}")
async def websocket_stream(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    db = SessionLocal()

    try:
        thresholds = get_thresholds_from_db(db)
        ctx = get_session_context(session_id)

        # If no session context exists, create one (webcam sessions start here)
        if ctx is None:
            create_session(db, name=f"Webcam {session_id[:8]}", source_type="WEBCAM",
                           thresholds=thresholds)
            ctx = get_session_context(session_id)

        smoother = ctx["smoother"]
        state_machine = ctx["state_machine"]
        alert_engine = ctx["alert_engine"]

        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)
            msg_type = msg.get("type", "")

            if msg_type == "FRAME_SUBMIT":
                payload = msg.get("payload", {})
                b64 = payload.get("frame_b64", "")
                bgr = decode_b64_to_bgr(b64)

                if bgr is None:
                    await websocket.send_text(json.dumps({
                        "type": "ERROR",
                        "payload": {"code": "DECODE_ERROR",
                                    "message": "Could not decode frame", "recoverable": True}
                    }))
                    continue

                result = run_pipeline(bgr, smoother, state_machine, alert_engine)
                frame_index = increment_frame(session_id)
                ts = now_ms()

                # Refresh thresholds (may have changed via Settings)
                thresholds = get_thresholds_from_db(db)
                state_machine.update_thresholds(thresholds)
                alert_engine.update_cooldown(thresholds.alert_cooldown_seconds)

                row = build_metric_row(
                    session_id=session_id, frame_index=frame_index,
                    timestamp_ms=ts, source_type="WEBCAM", result=result
                )
                append_row_to_csv(session_id, row)
                store_frame_to_db(db, row)

                telegram_sent_codes = set()
                if thresholds.telegram_enabled and result.alerts:
                    for alert in result.alerts:
                        frame_bytes = base64.b64decode(result.annotated_frame_b64)
                        sent = await send_telegram_alert(
                            alert_code=alert.code,
                            severity=alert.severity,
                            message=alert.message,
                            session_name=f"Webcam {session_id[:8]}",
                            grill_state=result.grill_state,
                            metrics={
                                "L_star_mean": result.raw_metrics.L_star_mean,
                                "browning_score": result.raw_metrics.browning_score,
                                "burn_risk_area_pct": result.raw_metrics.burn_risk_area_pct,
                                "smoke_density": result.raw_metrics.smoke_density,
                            },
                            annotated_frame_bytes=frame_bytes if alert.severity == "CRITICAL" else None,
                            bot_token=thresholds.telegram_bot_token,
                            chat_id=thresholds.telegram_chat_id,
                        )
                        if sent:
                            telegram_sent_codes.add(alert.code)

                store_events_to_db(db, session_id, frame_index, result, telegram_sent_codes)
                db.commit()

                # Build and send WS response
                response = {
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
                            {"code": a.code, "severity": a.severity,
                             "message": a.message, "telegram_sent": a.code in telegram_sent_codes}
                            for a in result.alerts
                        ],
                    }
                }
                await websocket.send_text(json.dumps(response))

                if result.state_changed:
                    await websocket.send_text(json.dumps({
                        "type": "STATE_CHANGE",
                        "payload": {
                            "session_id": session_id,
                            "from_state": result.prev_state,
                            "to_state": result.grill_state,
                            "frame_index": frame_index,
                        }
                    }))

                for alert in result.alerts:
                    await websocket.send_text(json.dumps({
                        "type": "ALERT",
                        "payload": {
                            "session_id": session_id,
                            "alert_code": alert.code,
                            "severity": alert.severity,
                            "message": alert.message,
                            "telegram_sent": alert.code in telegram_sent_codes,
                            "frame_index": frame_index,
                        }
                    }))

            elif msg_type == "CONTROL":
                action = msg.get("payload", {}).get("action", "")
                if action == "STOP":
                    await websocket.send_text(json.dumps({
                        "type": "ACK", "payload": {"action": "STOP", "status": "OK"}
                    }))
                    break
                await websocket.send_text(json.dumps({
                    "type": "ACK", "payload": {"action": action, "status": "OK"}
                }))

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: %s", session_id)
    except Exception as exc:
        logger.exception("WebSocket error for session %s: %s", session_id, exc)
    finally:
        manager.disconnect(session_id)
        db.close()
