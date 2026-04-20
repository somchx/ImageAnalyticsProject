import time
from datetime import datetime, timezone


def now_ms() -> int:
    """Current UTC time as Unix epoch milliseconds."""
    return int(time.time() * 1000)


def elapsed_str(start_ms: int) -> str:
    """Human-readable elapsed time from start_ms epoch-ms to now."""
    elapsed = (now_ms() - start_ms) / 1000.0
    h = int(elapsed // 3600)
    m = int((elapsed % 3600) // 60)
    s = int(elapsed % 60)
    return f"{h:02d}:{m:02d}:{s:02d}"


def utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
