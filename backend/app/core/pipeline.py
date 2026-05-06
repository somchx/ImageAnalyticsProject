"""
Master CV pipeline orchestrator.
Runs every processing step in order and returns a complete FrameResult.
No AI/ML — all steps are traditional image processing.
"""

import time
import base64
from dataclasses import dataclass, field
from typing import List, Optional
import numpy as np
import cv2

from app.core.dehazing import dark_channel_prior_dehaze
from app.core.colorspace import normalize_frame, extract_food_roi, bgr_to_lab_roi
from app.core.smoke_detector import estimate_smoke_density
from app.core.metrics import compute_metrics, RawMetrics
from app.core.smoother import MovingAverageSmoother
from app.core.state_machine import GrillState, GrillStateMachine, SmoothedSnapshot
from app.core.alert_engine import AlertEngine, AlertPayload


@dataclass
class FrameResult:
    raw_metrics: RawMetrics
    smoothed: dict
    grill_state: str
    prev_state: str
    state_changed: bool
    alerts: List[AlertPayload]
    explanation: str
    annotated_frame_b64: str  # base64 JPEG
    dehazed_frame_b64: str
    roi_mask_b64: str
    processing_time_ms: float


def run_pipeline(
    bgr_frame: np.ndarray,
    smoother: MovingAverageSmoother,
    state_machine: GrillStateMachine,
    alert_engine: AlertEngine,
) -> FrameResult:
    t0 = time.perf_counter()

    # 1. Normalize
    frame = normalize_frame(bgr_frame)

    # 2. DCP dehaze
    dehazed = dark_channel_prior_dehaze(frame)

    # 3. ROI extraction
    roi_mask, roi_pixel_count = extract_food_roi(dehazed)

    # 4. CIELAB conversion → ROI pixel arrays
    roi_L, roi_a, roi_b = bgr_to_lab_roi(dehazed, roi_mask)

    # 5. Smoke density
    l_std = float(np.std(roi_L)) if len(roi_L) > 0 else 0.0
    smoke_density = estimate_smoke_density(frame, l_std)

    # 6. Compute raw metrics
    raw = compute_metrics(roi_L, roi_a, roi_b, roi_pixel_count)
    raw.smoke_density = smoke_density

    # 7. Temporal smoothing
    smoothed_dict = smoother.update({
        "L_star_smooth": raw.L_star_mean,
        "browning_smooth": raw.browning_score,
        "cooked_area_smooth": raw.cooked_area_pct,
        "burn_risk_smooth": raw.burn_risk_area_pct,
        "char_area_smooth": raw.char_area_pct,
        "smoke_smooth": raw.smoke_density,
    })
    snap = SmoothedSnapshot(**smoothed_dict)

    # 8. State machine
    prev_state = state_machine.state
    state, state_changed = state_machine.update(snap)

    # 9. Alert engine
    alerts = alert_engine.evaluate(snap, state, state_changed)

    # 10. Generate explanation
    explanation = _generate_explanation(state, snap, alerts, state_changed, prev_state)

    # 11. Annotate frame
    annotated = _annotate_frame(dehazed.copy(), roi_mask, roi_L, state, snap)
    dehazed_b64 = _encode_jpeg(dehazed)
    annotated_b64 = _encode_jpeg(annotated)
    mask_vis = cv2.cvtColor(roi_mask, cv2.COLOR_GRAY2BGR)
    mask_b64 = _encode_jpeg(mask_vis)

    processing_time_ms = (time.perf_counter() - t0) * 1000.0

    return FrameResult(
        raw_metrics=raw,
        smoothed=smoothed_dict,
        grill_state=state.value,
        prev_state=prev_state.value,
        state_changed=state_changed,
        alerts=alerts,
        explanation=explanation,
        annotated_frame_b64=annotated_b64,
        dehazed_frame_b64=dehazed_b64,
        roi_mask_b64=mask_b64,
        processing_time_ms=processing_time_ms,
    )


def _annotate_frame(
    frame: np.ndarray,
    roi_mask: np.ndarray,
    roi_L: np.ndarray,
    state: GrillState,
    snap: SmoothedSnapshot,
) -> np.ndarray:
    h, w = frame.shape[:2]

    # Draw ROI contour in green
    contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame, contours, -1, (0, 255, 0), 2)

    # Dual-layer burn overlay:
    #   - True char (L*<22, |a*|<6, |b*|<6): solid red
    #   - Overcooked/dark zone (L*<30, not char): orange tint
    if len(roi_L) > 0:
        lab  = cv2.cvtColor(frame, cv2.COLOR_BGR2Lab)
        L_ch = lab[:, :, 0].astype(np.float64) / 2.55
        a_ch = lab[:, :, 1].astype(np.float64) - 128.0
        b_ch = lab[:, :, 2].astype(np.float64) - 128.0
        in_roi    = roi_mask > 0
        char_mask = (
            (L_ch < 22.0) & (np.abs(a_ch) < 6.0) & (np.abs(b_ch) < 6.0) & in_roi
        ).astype(np.uint8) * 255
        dark_mask = ((L_ch < 30.0) & in_roi & (char_mask == 0)).astype(np.uint8) * 255
        overlay = frame.copy()
        overlay[dark_mask > 0] = (0, 100, 255)   # orange = overcooked risk
        overlay[char_mask > 0] = (0,   0, 220)   # red    = true char
        frame = cv2.addWeighted(frame, 0.65, overlay, 0.35, 0)

    # State text
    state_color = _state_color(state)
    cv2.rectangle(frame, (0, 0), (w, 36), (20, 20, 20), -1)
    cv2.putText(frame, f"State: {state.value}", (8, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, state_color, 2, cv2.LINE_AA)

    # Browning bar at bottom
    bar_w = int(snap.browning_smooth * w)
    bar_color = _browning_bar_color(snap.browning_smooth)
    cv2.rectangle(frame, (0, h - 14), (w, h), (30, 30, 30), -1)
    cv2.rectangle(frame, (0, h - 14), (bar_w, h), bar_color, -1)
    cv2.putText(frame, f"Browning: {snap.browning_smooth:.2f}", (4, h - 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (230, 230, 230), 1, cv2.LINE_AA)

    # Smoke indicator top-right
    smoke_label = "Smoke: " + ("HIGH" if snap.smoke_smooth > 0.55
                               else "MED" if snap.smoke_smooth > 0.30 else "LOW")
    smoke_color = (0, 0, 200) if snap.smoke_smooth > 0.55 else \
        (0, 165, 255) if snap.smoke_smooth > 0.30 else (0, 200, 0)
    cv2.putText(frame, smoke_label, (w - 150, 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, smoke_color, 1, cv2.LINE_AA)

    return frame


def _state_color(state: GrillState):
    return {
        GrillState.RAW: (180, 180, 180),
        GrillState.COOKING: (0, 200, 255),
        GrillState.READY_TO_FLIP: (0, 165, 255),
        GrillState.READY: (0, 220, 0),
        GrillState.OVERCOOKED_RISK: (0, 100, 255),
        GrillState.BURNT: (0, 0, 220),
    }.get(state, (255, 255, 255))


def _browning_bar_color(score: float):
    if score < 0.40:
        return (0, 200, 0)
    if score < 0.65:
        return (0, 200, 255)
    if score < 0.85:
        return (0, 100, 255)
    return (0, 0, 220)


def _encode_jpeg(frame: np.ndarray, quality: int = 75) -> str:
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf.tobytes()).decode("ascii")


def _generate_explanation(
    state: GrillState,
    snap: SmoothedSnapshot,
    alerts: List[AlertPayload],
    state_changed: bool,
    prev_state: GrillState,
) -> str:
    parts = []

    if state_changed and prev_state != state:
        parts.append(f"State changed from {prev_state.value} to {state.value}.")

    if state == GrillState.READY_TO_FLIP:
        parts.append(
            f"Flip recommended: browning score reached {snap.browning_smooth:.2f} "
            f"(threshold 0.40) and L* dropped to {snap.L_star_smooth:.1f}."
        )
    elif state == GrillState.OVERCOOKED_RISK:
        parts.append(
            f"Overcooked risk: browning={snap.browning_smooth:.2f}, L*={snap.L_star_smooth:.1f}. "
            "Remove pork soon to avoid burning."
        )
    elif state == GrillState.BURNT:
        parts.append(
            f"Burnt detected: L*={snap.L_star_smooth:.1f} (threshold 22.0) or "
            f"char area={snap.char_area_smooth:.1f}% (threshold 20%). Remove immediately."
        )

    for alert in alerts:
        if alert.code == "BURN_RISK_HIGH":
            parts.append(
                f"Burn risk warning: {snap.burn_risk_smooth:.1f}% of surface has L*<30 "
                "for 3 consecutive frames."
            )
        elif alert.code == "BURN_RISK_CRITICAL":
            parts.append(
                f"Critical burn risk: {snap.burn_risk_smooth:.1f}% of surface is at risk "
                f"and L*={snap.L_star_smooth:.1f}."
            )
        elif alert.code == "SMOKE_SPIKE":
            parts.append(
                f"Smoke detected (density={snap.smoke_smooth:.2f}): "
                "analysis confidence is MEDIUM."
            )
        elif alert.code == "SMOKE_CRITICAL":
            parts.append(
                f"Heavy smoke (density={snap.smoke_smooth:.2f}): "
                "confidence is LOW — metrics may be unreliable."
            )

    if not parts:
        parts.append(
            f"Normal monitoring. State: {state.value}. "
            f"L*={snap.L_star_smooth:.1f}, Browning={snap.browning_smooth:.2f}, "
            f"Burn risk={snap.burn_risk_smooth:.1f}%, Smoke={snap.smoke_smooth:.2f}."
        )

    return " ".join(parts)
