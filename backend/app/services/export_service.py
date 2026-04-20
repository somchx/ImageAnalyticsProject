import io
import csv
from pathlib import Path

from app.config import settings
from app.utils.csv_writer import CSV_FIELDS, get_csv_path


def generate_csv_content(session_id: str) -> str:
    """Return CSV file content as string. Falls back to DB query if CSV missing."""
    csv_path = get_csv_path(session_id)
    if csv_path.exists():
        return csv_path.read_text(encoding="utf-8")

    # Return empty CSV with header if no data yet
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=CSV_FIELDS)
    writer.writeheader()
    return output.getvalue()
