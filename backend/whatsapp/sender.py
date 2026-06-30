"""Send WhatsApp messages via Meta Cloud API (Graph v21.0)."""

import httpx
from config import settings

_GRAPH_BASE = "https://graph.facebook.com/v21.0"


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {settings.whatsapp_access_token}",
        "Content-Type": "application/json",
    }


async def _post(payload: dict) -> None:
    if not settings.whatsapp_phone_number_id or not settings.whatsapp_access_token:
        raise RuntimeError("WhatsApp credentials not configured in environment")
    url = f"{_GRAPH_BASE}/{settings.whatsapp_phone_number_id}/messages"
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(url, json=payload, headers=_headers())
        r.raise_for_status()


async def send_text(to: str, body: str) -> None:
    await _post({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": to,
        "type": "text",
        "text": {"body": body, "preview_url": False},
    })


async def send_buttons(to: str, body: str, buttons: list[dict]) -> None:
    """
    Show up to 3 quick-reply buttons.
    buttons = [{"id": "btn_id", "title": "Label"}, ...]
    Titles are capped at 20 chars (WhatsApp limit).
    """
    await _post({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": b["id"], "title": b["title"][:20]}}
                    for b in buttons[:3]
                ]
            },
        },
    })


async def send_list(to: str, body: str, button_label: str, sections: list[dict]) -> None:
    """
    Show a scrollable list picker.
    sections = [{"title": "Section", "rows": [{"id": "...", "title": "...", "description": "..."}]}]
    Rows titles capped at 24 chars, descriptions at 72 chars (WhatsApp limits).
    Max 10 rows total.
    """
    # Enforce WhatsApp field-length limits
    clean_sections = []
    for sec in sections:
        clean_rows = []
        for row in sec.get("rows", []):
            clean_rows.append({
                "id": row["id"],
                "title": row.get("title", "")[:24],
                "description": row.get("description", "")[:72],
            })
        if clean_rows:
            clean_sections.append({"title": sec.get("title", "")[:24], "rows": clean_rows})

    await _post({
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {"text": body},
            "action": {
                "button": button_label[:20],
                "sections": clean_sections,
            },
        },
    })
