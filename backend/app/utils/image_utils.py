import base64
import numpy as np
import cv2
from typing import Optional


def decode_b64_to_bgr(b64_str: str) -> Optional[np.ndarray]:
    """Decode a base64 JPEG/PNG string to a BGR numpy array."""
    try:
        data = base64.b64decode(b64_str)
        arr = np.frombuffer(data, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame
    except Exception:
        return None


def encode_bgr_to_b64(bgr_frame: np.ndarray, quality: int = 75) -> str:
    """Encode a BGR numpy array to a base64 JPEG string."""
    _, buf = cv2.imencode(".jpg", bgr_frame, [cv2.IMWRITE_JPEG_QUALITY, quality])
    return base64.b64encode(buf.tobytes()).decode("ascii")


def bytes_to_bgr(raw_bytes: bytes) -> Optional[np.ndarray]:
    """Decode raw image bytes (JPEG/PNG) to BGR numpy array."""
    try:
        arr = np.frombuffer(raw_bytes, dtype=np.uint8)
        return cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except Exception:
        return None
