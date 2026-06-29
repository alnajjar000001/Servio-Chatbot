from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import ChatRequest, ChatResponse
from orchestrator import run_orchestration

app = FastAPI(title="Servio AI Backend", version="2.0.0")

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
