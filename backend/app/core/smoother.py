"""
Temporal smoothing via moving average over a sliding window.
Reduces per-frame noise caused by lighting fluctuations or smoke transients.
"""

from collections import defaultdict, deque
from typing import Dict
import numpy as np


class MovingAverageSmoother:
    def __init__(self, window: int = 7):
        self.window = window
        self._buffers: Dict[str, deque] = defaultdict(lambda: deque(maxlen=self.window))

    def update(self, metrics: Dict[str, float]) -> Dict[str, float]:
        """Push new values and return smoothed dict."""
        smoothed = {}
        for key, value in metrics.items():
            self._buffers[key].append(float(value))
            smoothed[key] = float(np.mean(self._buffers[key]))
        return smoothed

    def reset(self):
        self._buffers.clear()
