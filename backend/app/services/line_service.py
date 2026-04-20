"""
LINE Messaging API stub — placeholder for future integration.
Implements the same interface as telegram_service for drop-in replacement.

To implement LINE integration:
  1. Install `line-bot-sdk`
  2. Set LINE_CHANNEL_ACCESS_TOKEN and LINE_USER_ID env vars
  3. Use LineBot API to push TextMessage / ImageMessage
  4. Replace NotImplementedError with actual API calls
"""

from typing import Optional, Dict, Any


async def send_line_alert(
    alert_code: str,
    severity: str,
    message: str,
    session_name: str,
    grill_state: str,
    metrics: Dict[str, Any],
    annotated_frame_bytes: Optional[bytes],
    channel_access_token: str,
    user_id: str,
) -> bool:
    raise NotImplementedError(
        "LINE Messaging API integration is not yet implemented. "
        "Install line-bot-sdk and implement using the same interface as telegram_service."
    )
