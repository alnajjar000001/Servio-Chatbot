"""
WhatsApp Business Cloud API webhook.

GET  /webhook/whatsapp  — Meta verification handshake
POST /webhook/whatsapp  — incoming messages from Meta
"""

import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import PlainTextResponse

from config import settings
from models.schemas import ChatMessage, MessageRole
from orchestrator import run_orchestration
from whatsapp.sender import send_text
from whatsapp.session_store import store

log = logging.getLogger(__name__)
router = APIRouter(prefix="/webhook", tags=["WhatsApp"])

_FALLBACK = (
    "Sorry, I'm having trouble right now. "
    "Please try again or contact our support line."
)


# ─── Verification handshake (Meta calls this once when you register the webhook) ─

@router.get("/whatsapp", response_class=PlainTextResponse)
async def verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge"),
) -> str:
    if mode == "subscribe" and token == settings.whatsapp_verify_token:
        log.info("WhatsApp webhook verified successfully")
        return challenge or ""
    raise HTTPException(status_code=403, detail="Invalid verify token")


# ─── Incoming messages ────────────────────────────────────────────────────────

@router.post("/whatsapp", status_code=200)
async def receive(request: Request, bg: BackgroundTasks) -> dict:
    """
    Meta requires a 200 response within ~5 s.
    We acknowledge immediately and process each message as a background task.
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
                if msg.get("type") != "text":
                    continue  # ignore image/audio/sticker etc. for now
                sender  = msg.get("from", "")
                text    = msg.get("text", {}).get("body", "").strip()
                msg_id  = msg.get("id", "")
                if sender and text:
                    bg.add_task(_handle_message, sender, text, msg_id)

    return {"status": "ok"}


# ─── Background handler ───────────────────────────────────────────────────────

async def _handle_message(sender: str, text: str, msg_id: str) -> None:
    # Drop exact duplicates (Meta sometimes delivers the same message twice)
    if store.is_duplicate(sender, msg_id):
        return

    session = store.get(sender)
    history = [
        ChatMessage(role=MessageRole(m["role"]), content=m["content"])
        for m in session.conversation_history
    ]

    try:
        reply, _, _, updated_ctx = await run_orchestration(
            user_message=text,
            conversation_history=history,
            session_context=session.session_context,
        )
        session.session_context = updated_ctx
        store.append_turn(sender, text, reply)
    except Exception as exc:
        log.error("Orchestration error for %s: %s", sender, exc)
        reply = _FALLBACK

    try:
        await send_text(sender, reply)
    except Exception as exc:
        log.error("Failed to send WhatsApp reply to %s: %s", sender, exc)
