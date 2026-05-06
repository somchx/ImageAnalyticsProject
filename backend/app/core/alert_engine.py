"""
Alert engine with per-code cooldown timers and consecutive-frame debouncing.
Generates human-readable alert messages for each event.
No AI/ML — rule-based threshold comparisons.
"""

import time
from dataclasses import dataclass, field
from typing import List, Dict

from app.core.state_machine import GrillState, SmoothedSnapshot


@dataclass
class AlertPayload:
    code: str
    severity: str  # WARNING | CRITICAL
    message: str
    trigger_metric: str = ""
    trigger_value: float = 0.0
    trigger_threshold: float = 0.0


class AlertEngine:
    def __init__(self, cooldown_seconds: float = 30.0):
        self.cooldown_seconds = cooldown_seconds
        self._last_fired: Dict[str, float] = {}
        self._consecutive: Dict[str, int] = {}

    def update_cooldown(self, cooldown_seconds: float):
        self.cooldown_seconds = cooldown_seconds

    def evaluate(
        self,
        smoothed: SmoothedSnapshot,
        state: GrillState,
        state_changed: bool,
    ) -> List[AlertPayload]:
        alerts: List[AlertPayload] = []
        now = time.time()

        def try_fire(
            code: str,
            severity: str,
            message: str,
            trigger_metric: str = "",
            trigger_value: float = 0.0,
            trigger_threshold: float = 0.0,
            required_consecutive: int = 1,
        ):
            last = self._last_fired.get(code, 0.0)
            if (now - last) < self.cooldown_seconds:
                self._consecutive[code] = 0  # reset streak while in cooldown
                return
            cnt = self._consecutive.get(code, 0) + 1
            self._consecutive[code] = cnt
            if cnt >= required_consecutive:
                self._last_fired[code] = now
                self._consecutive[code] = 0
                alerts.append(AlertPayload(
                    code=code, severity=severity, message=message,
                    trigger_metric=trigger_metric, trigger_value=trigger_value,
                    trigger_threshold=trigger_threshold,
                ))

        # State-change alerts (single frame)
        if state_changed:
            if state == GrillState.READY_TO_FLIP:
                try_fire("READY_TO_FLIP", "WARNING",
                         "Time to flip the pork! One side is evenly browned.",
                         "browning_score", smoothed.browning_smooth, 0.40)
            elif state == GrillState.READY:
                try_fire("READY", "WARNING",
                         "Pork is ready! Remove from grill now.",
                         "browning_score", smoothed.browning_smooth, 0.55)
            elif state == GrillState.OVERCOOKED_RISK:
                try_fire("OVERCOOKED_RISK", "WARNING",
                         "Overcooked risk! Remove pork very soon.",
                         "browning_score", smoothed.browning_smooth, 0.72)
            elif state == GrillState.BURNT:
                try_fire("BURNT", "CRITICAL",
                         "ALERT: Pork is burnt! Remove immediately.",
                         "L_star_mean", smoothed.L_star_smooth, 22.0)

        # Metric-based alerts (require consecutive frames)
        # CRITICAL: true char pixels (ashen, L*<22, |a*|<6, |b*|<6) OR very low L*
        if smoothed.char_area_smooth > 10.0 or smoothed.L_star_smooth < 22.0:
            try_fire("BURN_RISK_CRITICAL", "CRITICAL",
                     f"Critical burn risk! {smoothed.char_area_smooth:.1f}% char area detected.",
                     "char_area_pct", smoothed.char_area_smooth, 10.0,
                     required_consecutive=2)
        elif smoothed.burn_risk_smooth > 25.0:
            # Dark-but-not-char zone (threshold raised from 10 → 25 to reduce false positives)
            try_fire("BURN_RISK_HIGH", "WARNING",
                     f"Burn risk area at {smoothed.burn_risk_smooth:.1f}% — reduce heat.",
                     "burn_risk_area_pct", smoothed.burn_risk_smooth, 25.0,
                     required_consecutive=3)

        if smoothed.smoke_smooth > 0.55:
            try_fire("SMOKE_CRITICAL", "CRITICAL",
                     f"Heavy smoke! Density={smoothed.smoke_smooth:.2f}. Possible flare-up.",
                     "smoke_density", smoothed.smoke_smooth, 0.55,
                     required_consecutive=2)
        elif smoothed.smoke_smooth > 0.30:
            try_fire("SMOKE_SPIKE", "WARNING",
                     f"Smoke detected (density={smoothed.smoke_smooth:.2f}). Check grill.",
                     "smoke_density", smoothed.smoke_smooth, 0.30,
                     required_consecutive=3)

        return alerts

    def reset(self):
        self._last_fired.clear()
        self._consecutive.clear()
