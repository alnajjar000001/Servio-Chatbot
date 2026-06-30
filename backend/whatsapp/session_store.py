"""
In-memory WhatsApp session store.
Each WhatsApp user (identified by phone number) gets their own conversation
history and session context so the orchestrator stays fully stateless.
Sessions expire after 24 hours of inactivity.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from models.schemas import SessionContext


@dataclass
class WASession:
    conversation_history: list[dict] = field(default_factory=list)
    session_context: SessionContext = field(default_factory=SessionContext)
    last_active: datetime = field(default_factory=datetime.utcnow)
    processed_ids: set[str] = field(default_factory=set)


class SessionStore:
    _TTL = timedelta(hours=24)
    _MAX_HISTORY = 40   # keep last 20 turns (user + assistant pairs)

    def __init__(self) -> None:
        self._store: dict[str, WASession] = {}

    def get(self, phone: str) -> WASession:
        self._evict()
        if phone not in self._store:
            self._store[phone] = WASession()
        s = self._store[phone]
        s.last_active = datetime.utcnow()
        return s

    def is_duplicate(self, phone: str, msg_id: str) -> bool:
        """Return True and skip processing if this message ID was already handled."""
        s = self.get(phone)
        if msg_id in s.processed_ids:
            return True
        s.processed_ids.add(msg_id)
        # Prevent unbounded growth of the seen-IDs set
        if len(s.processed_ids) > 500:
            s.processed_ids = set(list(s.processed_ids)[-100:])
        return False

    def append_turn(self, phone: str, user_msg: str, ai_msg: str) -> None:
        s = self.get(phone)
        s.conversation_history.extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": ai_msg},
        ])
        # Trim to last _MAX_HISTORY messages to stay within token limits
        s.conversation_history = s.conversation_history[-self._MAX_HISTORY:]

    def _evict(self) -> None:
        cutoff = datetime.utcnow() - self._TTL
        self._store = {k: v for k, v in self._store.items() if v.last_active >= cutoff}


# Module-level singleton — shared across all requests in the process
store = SessionStore()
