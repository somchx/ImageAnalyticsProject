"""
ROI extraction and CIELAB color space conversion.

Techniques used:
  - HSV inRange positive meat-color selection (Class 04)
  - HoughLinesP grill-bar exclusion (Class 05)
  - Histogram Backprojection from center reference region (Class 07)
  - connectedComponentsWithStats multi-piece labeling (Class 06)
  - Morphological OPEN/CLOSE cleanup (Class 06)
  - Fallback to original edge-exclusion strategy if nothing detected
"""

import numpy as np
import cv2
from typing import Tuple


# ── HSV ranges that cover raw/cooked pork hues (H in [0,180] OpenCV space) ──
# Segment A: H=0-35  → golden/brown/red-brown tones
# Segment B: H=155-180 → pink/red wrap-around (raw pork blush)
_MEAT_LOWER_A = np.array([0,   30,  40],  dtype=np.uint8)
_MEAT_UPPER_A = np.array([35, 255, 225],  dtype=np.uint8)
_MEAT_LOWER_B = np.array([155, 30,  80],  dtype=np.uint8)
_MEAT_UPPER_B = np.array([180, 200, 230], dtype=np.uint8)

# Metal grate: very low saturation and very low value
_GRATE_LOWER  = np.array([0,  0,  0],  dtype=np.uint8)
_GRATE_UPPER  = np.array([180, 50, 50], dtype=np.uint8)


def extract_food_roi(dehazed_bgr: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Returns (roi_mask, roi_pixel_count).
    roi_mask: binary uint8 image (255 = food pixel, 0 = background/grate).

    Pipeline:
      1. HoughLinesP — detect and mask grill bars
      2. HSV inRange — positive meat-color selection
      3. Histogram Backprojection — refine using center reference
      4. Combine evidence; subtract grate + grill lines
      5. Morphological OPEN → CLOSE cleanup
      6. connectedComponentsWithStats — keep all significant pieces
      7. Fallback to edge-exclusion strategy if nothing found
    """
    h, w = dehazed_bgr.shape[:2]
    hsv  = cv2.cvtColor(dehazed_bgr, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(dehazed_bgr, cv2.COLOR_BGR2GRAY)

    # ── 1. Grill-bar exclusion via HoughLinesP (Class 05) ─────────────────
    edges = cv2.Canny(gray, 50, 150)
    grill_line_mask = np.zeros((h, w), dtype=np.uint8)
    lines = cv2.HoughLinesP(
        edges, 1, np.pi / 180,
        threshold=60, minLineLength=w // 5, maxLineGap=15
    )
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            if angle < 25 or angle > 155:          # near-horizontal bars only
                cv2.line(grill_line_mask, (x1, y1), (x2, y2), 255, 8)
    grill_line_mask = cv2.dilate(
        grill_line_mask,
        cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5)),
        iterations=1,
    )

    # ── 2. Positive meat-color selection via HSV inRange (Class 04) ────────
    meat_mask = cv2.bitwise_or(
        cv2.inRange(hsv, _MEAT_LOWER_A, _MEAT_UPPER_A),
        cv2.inRange(hsv, _MEAT_LOWER_B, _MEAT_UPPER_B),
    )
    meat_mask = cv2.bitwise_and(meat_mask, cv2.bitwise_not(grill_line_mask))

    # ── 3. Histogram Backprojection (Class 07) ─────────────────────────────
    # Build a 2D H-S histogram from the center region (likely a meat piece)
    rh, rw = max(h // 6, 20), max(w // 6, 20)
    cy, cx = h // 2, w // 2
    ref   = hsv[cy - rh : cy + rh, cx - rw : cx + rw]
    h_hist = cv2.calcHist([ref], [0, 1], None, [36, 32], [0, 180, 0, 256])
    cv2.normalize(h_hist, h_hist, 0, 255, cv2.NORM_MINMAX)
    backproj = cv2.calcBackProject([hsv], [0, 1], h_hist, [0, 180, 0, 256], 1)
    # Smooth with disc kernel (as in ex07-6)
    disc = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    cv2.filter2D(backproj, -1, disc, backproj)
    _, bp_mask = cv2.threshold(backproj, 60, 255, cv2.THRESH_BINARY)
    bp_mask = bp_mask.astype(np.uint8)

    # ── 4. Combine evidence; remove dark grate + grill lines ───────────────
    grate_mask = cv2.inRange(hsv, _GRATE_LOWER, _GRATE_UPPER)
    not_grate  = cv2.bitwise_not(grate_mask)
    not_lines  = cv2.bitwise_not(grill_line_mask)

    combined = cv2.bitwise_or(meat_mask, bp_mask)
    combined = cv2.bitwise_and(combined, not_grate)
    combined = cv2.bitwise_and(combined, not_lines)

    # ── 5. Morphological cleanup ───────────────────────────────────────────
    open_k  = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7,  7))
    close_k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    combined = cv2.morphologyEx(combined, cv2.MORPH_OPEN,  open_k)
    combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, close_k)

    # ── 6. connectedComponentsWithStats — keep all significant pieces ───────
    #    (Class 06: ex06-6_connectedComponent.py)
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(
        combined, connectivity=8
    )
    min_area = max(200, int(h * w * 0.004))   # at least 0.4% of frame area
    roi_mask = np.zeros((h, w), dtype=np.uint8)
    for i in range(1, num_labels):            # label 0 = background
        if stats[i, cv2.CC_STAT_AREA] >= min_area:
            roi_mask[labels == i] = 255

    # ── 7. Fallback if positive detection found nothing ─────────────────────
    if np.sum(roi_mask) == 0:
        roi_mask = _fallback_roi(dehazed_bgr, h, w, hsv, gray)

    roi_pixel_count = int(np.sum(roi_mask > 0))
    if roi_pixel_count == 0:
        roi_pixel_count = 1

    return roi_mask, roi_pixel_count


def _fallback_roi(
    dehazed_bgr: np.ndarray,
    h: int, w: int,
    hsv: np.ndarray,
    gray: np.ndarray,
) -> np.ndarray:
    """Original edge-exclusion strategy, used only when positive detection yields nothing."""
    grate_mask   = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 50, 60]))
    edges        = cv2.Canny(gray, 50, 150)
    edge_kernel  = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated_edges = cv2.dilate(edges, edge_kernel, iterations=2)
    exclusion    = cv2.bitwise_or(grate_mask, dilated_edges)
    roi_mask     = cv2.bitwise_not(exclusion)
    open_k       = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    close_k      = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    roi_mask     = cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN,  open_k)
    roi_mask     = cv2.morphologyEx(roi_mask, cv2.MORPH_CLOSE, close_k)
    contours, _  = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        margin_h, margin_w = int(h * 0.2), int(w * 0.2)
        roi_mask = np.zeros((h, w), dtype=np.uint8)
        roi_mask[margin_h : h - margin_h, margin_w : w - margin_w] = 255
    else:
        largest  = max(contours, key=cv2.contourArea)
        roi_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(roi_mask, [largest], -1, 255, -1)
    return roi_mask


def bgr_to_lab_roi(
    dehazed_bgr: np.ndarray, roi_mask: np.ndarray
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Converts dehazed BGR image to CIE L*a*b* and returns
    (L_arr, a_arr, b_arr) as 1D float64 arrays of ROI pixels.

    OpenCV Lab encoding:
      L  ∈ [0, 255] → divide by 2.55 → true L* ∈ [0, 100]
      a  ∈ [0, 255] → subtract 128   → true a* ∈ [-128, 127]
      b  ∈ [0, 255] → subtract 128   → true b* ∈ [-128, 127]
    """
    lab  = cv2.cvtColor(dehazed_bgr, cv2.COLOR_BGR2Lab)
    L_ch = lab[:, :, 0].astype(np.float64) / 2.55
    a_ch = lab[:, :, 1].astype(np.float64) - 128.0
    b_ch = lab[:, :, 2].astype(np.float64) - 128.0

    mask = roi_mask > 0
    return L_ch[mask], a_ch[mask], b_ch[mask]


def normalize_frame(bgr_frame: np.ndarray, max_dim: int = 1280) -> np.ndarray:
    """Resize to max_dim on longest side; apply gentle Gaussian blur for JPEG noise."""
    h, w = bgr_frame.shape[:2]
    if max(h, w) > max_dim:
        scale    = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        bgr_frame = cv2.resize(bgr_frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(bgr_frame, (3, 3), 0)
