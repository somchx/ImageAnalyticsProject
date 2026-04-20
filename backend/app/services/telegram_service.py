"""
Telegram Bot notification service.
Sends text alerts (and optionally photo) via the Telegram Bot API.
Best-effort: never raises exceptions — errors are logged only.
"""

import logging
import asyncio
from typing import Optional, Dict, Any

import httpx

logger = logging.getLogger(__name__)

SEVERITY_EMOJI = {"WARNING": "⚠️", "CRITICAL": "🚨"}


async def send_telegram_alert(
    alert_code: str,
    severity: str,
    message: str,
    session_name: str,
    grill_state: str,
    metrics: Dict[str, Any],
    annotated_frame_bytes: Optional[bytes],
    bot_token: str,
    chat_id: str,
) -> bool:
    """
    Send an alert message (and optionally a photo) to a Telegram chat.
    Returns True on success, False on any error.
    """
    if not bot_token or not chat_id:
        logger.warning("Telegram not configured — skipping alert.")
        return False

    emoji = SEVERITY_EMOJI.get(severity, "🔔")
    elapsed = metrics.get("elapsed", "N/A")
    l_star = metrics.get("L_star_mean", 0.0)
    browning = metrics.get("browning_score", 0.0)
    burn_risk = metrics.get("burn_risk_area_pct", 0.0)
    smoke = metrics.get("smoke_density", 0.0)

    # Escape MarkdownV2 special chars
    def esc(s: str) -> str:
        for ch in r"_*[]()~`>#+-=|{}.!":
            s = s.replace(ch, f"\\{ch}")
        return s

    text = (
        f"{emoji} *Grill Alert — {esc(alert_code)}*\n\n"
        f"📊 *Session:* `{esc(session_name)}`\n"
        f"⏱ *Time:* `{esc(str(elapsed))}`\n"
        f"🔔 *Severity:* {emoji} {esc(severity)}\n\n"
        f"📈 *Current Metrics:*\n"
        f"• L\\* \\(brightness\\): `{l_star:.1f}`\n"
        f"• Browning score: `{browning:.2f}`\n"
        f"• Burn risk area: `{burn_risk:.1f}%`\n"
        f"• Smoke density: `{smoke:.2f}`\n\n"
        f"📍 *Grill State:* `{esc(grill_state)}`\n\n"
        f"_{esc(message)}_"
    )

    base_url = f"https://api.telegram.org/bot{bot_token}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            if annotated_frame_bytes and severity == "CRITICAL":
                resp = await client.post(
                    f"{base_url}/sendPhoto",
                    data={"chat_id": chat_id, "caption": text, "parse_mode": "MarkdownV2"},
                    files={"photo": ("frame.jpg", annotated_frame_bytes, "image/jpeg")},
                )
            else:
                resp = await client.post(
                    f"{base_url}/sendMessage",
                    json={"chat_id": chat_id, "text": text, "parse_mode": "MarkdownV2"},
                )
            if resp.status_code == 200:
                return True
            logger.warning("Telegram API error %d: %s", resp.status_code, resp.text)
            return False
    except Exception as exc:
        logger.warning("Telegram send failed: %s", exc)
        return False


async def send_test_message(bot_token: str, chat_id: str) -> bool:
    """Send a simple test message to verify credentials."""
    if not bot_token or not chat_id:
        return False
    base_url = f"https://api.telegram.org/bot{bot_token}"
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{base_url}/sendMessage",
                json={"chat_id": chat_id,
                      "text": "✅ Grill Analytics: Telegram notification configured successfully!"},
            )
            return resp.status_code == 200
    except Exception:
        return False
