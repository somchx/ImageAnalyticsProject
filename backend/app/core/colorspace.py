"""
ROI extraction and CIELAB color space conversion.
Excludes grill grates and background; isolates the food item.
No AI/ML — morphological operations and contour analysis only.
"""

import numpy as np
import cv2
from typing import Tuple


def extract_food_roi(dehazed_bgr: np.ndarray) -> Tuple[np.ndarray, int]:
    """
    Returns (roi_mask, roi_pixel_count).
    roi_mask is a binary uint8 image (255 = food, 0 = background/grate).

    Strategy:
      1. Mask out dark grate metal via HSV thresholding
      2. Mask out grate line structure via edge detection + dilation
      3. Combine exclusion masks → invert → morphological cleanup
      4. Keep only the largest contour (main food item)
    """
    h, w = dehazed_bgr.shape[:2]
    hsv = cv2.cvtColor(dehazed_bgr, cv2.COLOR_BGR2HSV)

    # Grate metal: very low saturation, low value (dark gray/black metal)
    grate_mask = cv2.inRange(hsv, np.array([0, 0, 0]), np.array([180, 50, 60]))

    # Grate lines: strong parallel edges
    gray = cv2.cvtColor(dehazed_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dilated_edges = cv2.dilate(edges, edge_kernel, iterations=2)

    # Combine: anything that is grate-colored OR edge-structured is excluded
    exclusion = cv2.bitwise_or(grate_mask, dilated_edges)
    roi_mask = cv2.bitwise_not(exclusion)

    # Morphological cleanup to remove noise and fill holes
    open_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
    roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_OPEN, open_kernel)
    roi_mask = cv2.morphologyEx(roi_mask, cv2.MORPH_CLOSE, close_kernel)

    # Keep largest contour only (the main food piece)
    contours, _ = cv2.findContours(roi_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        # Fallback: use center 60% of frame if no contour found
        margin_h = int(h * 0.2)
        margin_w = int(w * 0.2)
        roi_mask = np.zeros((h, w), dtype=np.uint8)
        roi_mask[margin_h:h - margin_h, margin_w:w - margin_w] = 255
    else:
        largest = max(contours, key=cv2.contourArea)
        roi_mask = np.zeros((h, w), dtype=np.uint8)
        cv2.drawContours(roi_mask, [largest], -1, 255, -1)

    roi_pixel_count = int(np.sum(roi_mask > 0))
    if roi_pixel_count == 0:
        roi_pixel_count = 1  # prevent division by zero

    return roi_mask, roi_pixel_count


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
    lab = cv2.cvtColor(dehazed_bgr, cv2.COLOR_BGR2Lab)
    L_ch = lab[:, :, 0].astype(np.float64) / 2.55
    a_ch = lab[:, :, 1].astype(np.float64) - 128.0
    b_ch = lab[:, :, 2].astype(np.float64) - 128.0

    mask = roi_mask > 0
    return L_ch[mask], a_ch[mask], b_ch[mask]


def normalize_frame(bgr_frame: np.ndarray, max_dim: int = 1280) -> np.ndarray:
    """Resize to max_dim on longest side; apply gentle Gaussian blur for JPEG noise."""
    h, w = bgr_frame.shape[:2]
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        new_w, new_h = int(w * scale), int(h * scale)
        bgr_frame = cv2.resize(bgr_frame, (new_w, new_h), interpolation=cv2.INTER_AREA)
    return cv2.GaussianBlur(bgr_frame, (3, 3), 0)
