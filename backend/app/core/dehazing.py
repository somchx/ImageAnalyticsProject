"""
Dark Channel Prior (DCP) dehazing — He et al. 2009.
Removes smoke/haze interference before color analysis.
No AI/ML — pure image processing.
"""

import numpy as np
import cv2


def dark_channel_prior_dehaze(
    bgr_img: np.ndarray,
    patch_size: int = 15,
    omega: float = 0.95,
    t_min: float = 0.1,
) -> np.ndarray:
    """
    Removes haze from a BGR image using the Dark Channel Prior.

    Steps:
      1. Compute dark channel (min over local patch of min over BGR channels)
      2. Estimate atmospheric light A from top brightest dark-channel pixels
      3. Compute transmission map t
      4. Refine t with guided box blur
      5. Recover scene radiance J

    Returns dehazed BGR uint8 image.
    """
    img = bgr_img.astype(np.float64) / 255.0
    h, w = img.shape[:2]

    # --- Step 1: dark channel ---
    dark = _compute_dark_channel(img, patch_size)

    # --- Step 2: atmospheric light ---
    A = _estimate_atmospheric_light(img, dark)

    # --- Step 3: transmission map ---
    normalized = img / A  # element-wise divide per channel
    dark_norm = _compute_dark_channel(normalized, patch_size)
    t = 1.0 - omega * dark_norm
    t = np.clip(t, t_min, 1.0)

    # --- Step 4: guided filter approximation (large box blur) ---
    gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY).astype(np.float64) / 255.0
    t = _guided_filter_approx(gray, t, radius=40, eps=1e-3)
    t = np.clip(t, t_min, 1.0)

    # --- Step 5: recover scene radiance ---
    t3 = t[:, :, np.newaxis]
    J = (img - A) / t3 + A
    J = np.clip(J, 0.0, 1.0)
    return (J * 255).astype(np.uint8)


def _compute_dark_channel(img: np.ndarray, patch_size: int) -> np.ndarray:
    min_channel = np.min(img, axis=2)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (patch_size, patch_size))
    dark = cv2.erode(min_channel.astype(np.float32), kernel)
    return dark.astype(np.float64)


def _estimate_atmospheric_light(img: np.ndarray, dark: np.ndarray) -> np.ndarray:
    h, w = dark.shape
    n_pixels = h * w
    n_bright = max(1, int(n_pixels * 0.001))  # top 0.1%

    flat_dark = dark.flatten()
    flat_img = img.reshape(n_pixels, 3)

    indices = np.argsort(flat_dark)[-n_bright:]
    A = np.mean(flat_img[indices], axis=0)
    # Clamp to avoid division-by-zero and over-correction
    A = np.clip(A, 200 / 255.0, 1.0)
    return A.reshape(1, 1, 3)


def _guided_filter_approx(
    guide: np.ndarray, src: np.ndarray, radius: int, eps: float
) -> np.ndarray:
    """
    Fast guided filter via box blur approximation (Kaiming He fast version).
    guide and src are float64 single-channel images in [0,1].
    """
    r = radius
    g = guide.astype(np.float32)
    p = src.astype(np.float32)

    mean_g = cv2.blur(g, (r, r))
    mean_p = cv2.blur(p, (r, r))
    mean_gp = cv2.blur(g * p, (r, r))
    mean_gg = cv2.blur(g * g, (r, r))

    cov_gp = mean_gp - mean_g * mean_p
    var_g = mean_gg - mean_g * mean_g

    a = cov_gp / (var_g + eps)
    b = mean_p - a * mean_g

    mean_a = cv2.blur(a, (r, r))
    mean_b = cv2.blur(b, (r, r))

    return (mean_a * g + mean_b).astype(np.float64)
