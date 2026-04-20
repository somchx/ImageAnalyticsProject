"""
Smoke / haze density estimator.
Uses sky-band brightness uniformity + local contrast drop.
No AI/ML — rule-based signal analysis.
"""

import numpy as np
import cv2


def estimate_smoke_density(bgr_frame: np.ndarray, lab_l_std: float) -> float:
    """
    Returns a smoke density score in [0.0, 1.0].
    0 = clear, 1 = very heavy smoke.

    Three sub-signals:
      1. Sky-band uniformity: top-20% rows are very uniform when smoke is dense
      2. Sky-band brightness: haze tends to brighten the upper portion
      3. Contrast drop: smoke reduces local contrast in the food area
    """
    h = bgr_frame.shape[0]
    sky_h = max(1, h // 5)
    sky_band = bgr_frame[:sky_h, :]

    gray_sky = cv2.cvtColor(sky_band, cv2.COLOR_BGR2GRAY).astype(np.float64)
    sky_mean = float(np.mean(gray_sky))
    sky_std = float(np.std(gray_sky))

    # Low std + high mean = uniform bright haze = smoke
    haze_uniformity = 1.0 - float(np.clip(sky_std / 30.0, 0.0, 1.0))
    haze_brightness = float(np.clip((sky_mean - 100.0) / 155.0, 0.0, 1.0))

    # Low L* std in food area = contrast drop due to haze
    contrast_drop = 1.0 - float(np.clip(lab_l_std / 30.0, 0.0, 1.0))

    smoke_density = (
        0.40 * haze_uniformity
        + 0.35 * haze_brightness
        + 0.25 * contrast_drop
    )
    return float(np.clip(smoke_density, 0.0, 1.0))
