"""
Per-frame metric computation from CIELAB ROI pixel arrays.
Browning score formula based on Maillard reaction color changes.
No AI/ML — pure arithmetic on CIE color values.
"""

import numpy as np
from dataclasses import dataclass


@dataclass
class RawMetrics:
    L_star_mean: float
    L_star_std: float
    a_star_mean: float
    a_star_std: float
    b_star_mean: float
    b_star_std: float
    browning_score: float
    cooked_area_pct: float
    burn_risk_area_pct: float
    smoke_density: float = 0.0


def compute_metrics(
    roi_L: np.ndarray,
    roi_a: np.ndarray,
    roi_b: np.ndarray,
    roi_pixel_count: int,
) -> RawMetrics:
    """
    Compute all per-frame metrics from CIE L*a*b* ROI pixel arrays.

    Browning score (0–1) composite:
      sig_L: darkness (raw pork L* ≈ 68–72; burnt < 22) — weight 0.50
      sig_a: redness increase from Maillard reaction — weight 0.30
      sig_b: yellowness increase from browning — weight 0.20

    Cooked area: pixels where L*<55 AND a*>4 (browned tissue)
    Burn risk area: pixels where L*<30 (dark/charred tissue)
    """
    if len(roi_L) == 0:
        return RawMetrics(
            L_star_mean=75.0, L_star_std=0.0,
            a_star_mean=2.0, a_star_std=0.0,
            b_star_mean=8.0, b_star_std=0.0,
            browning_score=0.0, cooked_area_pct=0.0,
            burn_risk_area_pct=0.0,
        )

    L_mean = float(np.mean(roi_L))
    L_std = float(np.std(roi_L))
    a_mean = float(np.mean(roi_a))
    a_std = float(np.std(roi_a))
    b_mean = float(np.mean(roi_b))
    b_std = float(np.std(roi_b))

    # Browning composite score
    sig_L = 1.0 - float(np.clip(L_mean / 75.0, 0.0, 1.0))
    sig_a = float(np.clip((a_mean - 2.0) / 20.0, 0.0, 1.0))
    sig_b = float(np.clip((b_mean - 8.0) / 25.0, 0.0, 1.0))
    browning_score = float(np.clip(0.50 * sig_L + 0.30 * sig_a + 0.20 * sig_b, 0.0, 1.0))

    # Pixel classifications
    n = roi_pixel_count
    cooked_pixels = int(np.sum((roi_L < 55.0) & (roi_a > 4.0)))
    burn_risk_pixels = int(np.sum(roi_L < 30.0))

    cooked_area_pct = float(cooked_pixels / n * 100.0)
    burn_risk_area_pct = float(burn_risk_pixels / n * 100.0)

    return RawMetrics(
        L_star_mean=L_mean,
        L_star_std=L_std,
        a_star_mean=a_mean,
        a_star_std=a_std,
        b_star_mean=b_mean,
        b_star_std=b_std,
        browning_score=browning_score,
        cooked_area_pct=cooked_area_pct,
        burn_risk_area_pct=burn_risk_area_pct,
    )
