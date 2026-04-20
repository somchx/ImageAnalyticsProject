from fastapi import APIRouter
from fastapi.responses import Response

from app.services.export_service import generate_csv_content

router = APIRouter()


@router.get("/csv/{session_id}")
def export_csv(session_id: str):
    content = generate_csv_content(session_id)
    return Response(
        content=content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{session_id}.csv"'},
    )
