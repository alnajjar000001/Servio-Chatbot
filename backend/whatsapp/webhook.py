"""
WhatsApp Business Cloud API webhook.
All traffic is routed through the menu-driven flow (no OpenAI involved).

GET  /webhook/whatsapp  — Meta verification handshake
POST /webhook/whatsapp  — incoming messages + interactive replies from Meta
"""

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from config import settings
from whatsapp.flow import handle
from whatsapp.sender import send_text
from whatsapp.session_store import store

log = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["WhatsApp"])


# ─── Verification handshake (called once when you register the webhook) ───────

@router.get("/whatsapp", response_class=PlainTextResponse)
async def verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
) -> str:
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        log.info("WhatsApp webhook verified")
        return challenge or ""
    raise HTTPException(status_code=403, detail="Invalid verify token")


# ─── Incoming messages ────────────────────────────────────────────────────────

@router.post("/whatsapp", status_code=200)
async def receive(request: Request, bg: BackgroundTasks) -> dict:
    """
    Meta requires a 200 response within ~5 s.
    Every message is dispatched as a background task so we return immediately.
    """
    try:
        data = await request.json()
    except Exception:
        return {"status": "ok"}

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            if change.get("field") != "messages":
                continue
            value = change.get("value", {})

            for msg in value.get("messages", []):
                sender   = msg.get("from", "")
                msg_id   = msg.get("id", "")
                msg_type = msg.get("type", "")

                text           = ""
                interactive_id = None

                if msg_type == "text":
                    text = msg.get("text", {}).get("body", "").strip()

                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    kind = interactive.get("type", "")
                    if kind == "button_reply":
                        interactive_id = interactive["button_reply"].get("id", "")
                        text           = interactive["button_reply"].get("title", "")
                    elif kind == "list_reply":
                        interactive_id = interactive["list_reply"].get("id", "")
                        text           = interactive["list_reply"].get("title", "")

                if sender and (text or interactive_id):
                    bg.add_task(_dispatch, sender, text, interactive_id, msg_id)

    return {"status": "ok"}


# ─── Background dispatcher ────────────────────────────────────────────────────

async def _dispatch(sender: str, text: str, interactive_id: str | None, msg_id: str) -> None:
    if store.is_duplicate(sender, msg_id):
        return
    try:
        await handle(sender, text, interactive_id)
    except Exception as exc:
        log.error("Flow error for %s: %s", sender, exc)
        try:
            await send_text(sender, "Sorry, something went wrong. Please type *hi* to start again.")
        except Exception:
            pass
