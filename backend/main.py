from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ChatRequest, ChatResponse
from orchestrator import run_orchestration
from whatsapp.webhook import router as whatsapp_router

app = FastAPI(title="Servio AI Backend", version="3.0.0")
app.include_router(whatsapp_router)

import os

_extra_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
_origins = [o.strip() for o in _extra_origins if o.strip()] + [
    "https://servio-chatbot.netlify.app",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "servio-ai-backend"}


@app.get("/debug/govs")
async def debug_govs(gov_id: str = "1"):
    """Temporary debug endpoint — shows raw API responses for governorates and areas."""
    from tools.get_governorates import execute_get_governorates
    from tools.get_areas import execute_get_areas_by_governorate

    govs_raw  = await execute_get_governorates()
    areas_raw = await execute_get_areas_by_governorate(governorate_id=gov_id)

    def _try_list(r):
        if isinstance(r, list):
            return r
        if isinstance(r, dict):
            raw = r.get("data")
            if isinstance(raw, list):
                return raw
            if isinstance(raw, dict):
                inner = raw.get("data")
                if isinstance(inner, list):
                    return inner
            for v in r.values():
                if isinstance(v, list):
                    return v
        return []

    govs_parsed  = _try_list(govs_raw)
    areas_parsed = _try_list(areas_raw)

    return {
        "governorates": {
            "raw": govs_raw,
            "parsed_count": len(govs_parsed),
            "first_item": govs_parsed[0] if govs_parsed else None,
        },
        "areas": {
            "gov_id_used": gov_id,
            "raw": areas_raw,
            "parsed_count": len(areas_parsed),
            "first_item": areas_parsed[0] if areas_parsed else None,
        },
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response_text, tool_calls, customer_data, updated_ctx = await run_orchestration(
            user_message=request.message,
            conversation_history=request.conversation_history,
            session_context=request.session_context,
        )
        return ChatResponse(
            response=response_text,
            tool_calls=tool_calls,
            customer_data=customer_data,
            session_context=updated_ctx,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
