"""
Rule-based grill state machine.
Transitions are driven by CIELAB browning metrics — no AI/ML.
States: RAW → COOKING → READY_TO_FLIP → READY → OVERCOOKED_RISK → BURNT
"""

from enum import Enum
from dataclasses import dataclass
from typing import Tuple

from app.models.schemas.settings import ThresholdSettings


class GrillState(str, Enum):
    RAW = "RAW"
    COOKING = "COOKING"
    READY_TO_FLIP = "READY_TO_FLIP"
    READY = "READY"
    OVERCOOKED_RISK = "OVERCOOKED_RISK"
    BURNT = "BURNT"


@dataclass
class SmoothedSnapshot:
    L_star_smooth: float
    browning_smooth: float
    cooked_area_smooth: float
    burn_risk_smooth: float
    smoke_smooth: float


class GrillStateMachine:
    MIN_HOLD_FRAMES = 5  # must stay in a state this long before advancing

    def __init__(self, thresholds: ThresholdSettings):
        self.state = GrillState.RAW
        self.prev_state = GrillState.RAW
        self.thresholds = thresholds
        self.hold_counter = 0

    def update(self, s: SmoothedSnapshot) -> Tuple[GrillState, bool]:
        """
        Evaluate transitions based on smoothed metrics.
        Returns (new_state, state_changed).
        """
        self.prev_state = self.state
        new_state = self._evaluate(s)
        changed = new_state != self.state
        if changed:
            self.state = new_state
            self.hold_counter = 0
        else:
            self.hold_counter += 1
        return self.state, changed

    def update_thresholds(self, thresholds: ThresholdSettings):
        self.thresholds = thresholds

    def _evaluate(self, s: SmoothedSnapshot) -> GrillState:
        t = self.thresholds

        # Emergency override — jump to BURNT from any state
        if s.L_star_smooth < 18.0 or s.burn_risk_smooth > 35.0:
            return GrillState.BURNT

        # Require minimum hold before advancing
        if self.hold_counter < self.MIN_HOLD_FRAMES:
            return self.state

        if self.state == GrillState.RAW:
            if s.L_star_smooth < t.l_star_cooking_max or s.browning_smooth > t.browning_cooking_min:
                return GrillState.COOKING

        elif self.state == GrillState.COOKING:
            if (s.browning_smooth >= t.browning_ready_to_flip_min
                    and s.L_star_smooth < t.l_star_ready_to_flip_max):
                return GrillState.READY_TO_FLIP

        elif self.state == GrillState.READY_TO_FLIP:
            # If browning drops sharply (fresh side after flip), go back to COOKING
            if s.browning_smooth < 0.30:
                return GrillState.COOKING
            if (s.browning_smooth >= t.browning_ready_min
                    and s.L_star_smooth < t.l_star_ready_max):
                return GrillState.READY

        elif self.state == GrillState.READY:
            if (s.browning_smooth >= t.browning_overcooked_min
                    and s.L_star_smooth < t.l_star_overcooked_max):
                return GrillState.OVERCOOKED_RISK

        elif self.state == GrillState.OVERCOOKED_RISK:
            if (s.browning_smooth >= t.browning_burnt_min
                    or s.L_star_smooth < t.l_star_burnt_max):
                return GrillState.BURNT

        return self.state
