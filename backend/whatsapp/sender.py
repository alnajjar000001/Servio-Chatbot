"""Send WhatsApp messages via Meta Cloud API (Graph v21.0)."""

import httpx
from config import settings

_GRAPH_BASE = "https://graph.facebook.com/v21.0"


async def send_text(to: str, body: str) -> None:
    """Send a plain-text WhatsApp message to `to` (E.164 format, no '+')."""
    if not settings.whatsapp_phone_number_id or not settings.whatsapp_access_token:
        raise RuntimeError("WhatsApp credentials not configured in environment")

    url = f"{_GRAPH_BASE}/{settings.whatsapp_phone_number_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": body, "preview_url": False},
    }
    headers = {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
