from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.db.database import get_db
from app.api.endpoints.settings import get_thresholds_from_db
from app.services.telegram_service import send_test_message

router = APIRouter()


@router.post("/telegram/test")
async def test_telegram(db: DBSession = Depends(get_db)):
    thresholds = get_thresholds_from_db(db)
    ok = await send_test_message(thresholds.telegram_bot_token, thresholds.telegram_chat_id)
    return {"success": ok, "message": "Test message sent" if ok else "Failed — check token and chat_id"}
