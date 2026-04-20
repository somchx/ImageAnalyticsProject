import csv
import os
from pathlib import Path
from typing import Dict, Any

from app.config import settings

CSV_FIELDS = [
    "session_id", "frame_index", "timestamp_ms", "source_type",
    "L_star_mean", "L_star_std", "a_star_mean", "a_star_std",
    "b_star_mean", "b_star_std",
    "browning_score", "cooked_area_pct", "burn_risk_area_pct", "smoke_density",
    "L_star_smooth", "browning_smooth", "cooked_area_smooth",
    "burn_risk_smooth", "smoke_smooth",
    "grill_state", "state_changed", "alert_codes",
    "processing_time_ms", "explanation",
]


def append_row_to_csv(session_id: str, row: Dict[str, Any]):
    path = Path(settings.data_dir) / f"{session_id}.csv"
    write_header = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS, extrasaction="ignore")
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def get_csv_path(session_id: str) -> Path:
    return Path(settings.data_dir) / f"{session_id}.csv"
