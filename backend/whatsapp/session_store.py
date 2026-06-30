"""
Per-user WhatsApp session: state machine + language preference + deduplication.
Sessions expire after 24 hours of inactivity.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

from models.schemas import SessionContext


class FlowState(str, Enum):
    SELECTING_LANG     = "selecting_lang"    # very first interaction — pick language
    IDLE               = "idle"
    AWAITING_PHONE     = "awaiting_phone"
    VERIFIED           = "verified"
    SELECTING_PROBLEM  = "selecting_problem"
    DESCRIBING_PROBLEM = "describing_problem"
    CONFIRMING_ORDER   = "confirming_order"
    REG_NAME           = "reg_name"
    REG_PHONE          = "reg_phone"
    REG_GOV            = "reg_gov"
    REG_AREA           = "reg_area"
    REG_BLOCK          = "reg_block"
    REG_STREET         = "reg_street"
    REG_CONFIRM        = "reg_confirm"


@dataclass
class RegData:
    """Fields collected during new-customer registration."""
    name: str = ""
    phone: str = ""
    gov_id: str = ""
    area_id: str = ""
    block: str = ""
    street: str = ""


@dataclass
class WASession:
    state: FlowState = FlowState.SELECTING_LANG   # start with language selection
    lang: str = "en"
    session_context: SessionContext = field(default_factory=SessionContext)
    reg: RegData = field(default_factory=RegData)

    # Pending service-request fields
    pending_problem_id: int = 0
    pending_description: str = ""

    # Temp caches: store full API objects so we use the correct IDs
    # regardless of which field name the API uses (id / governorateId / areaId …)
    gov_cache: list[dict] = field(default_factory=list)
    area_cache: list[dict] = field(default_factory=list)

    processed_ids: set[str] = field(default_factory=set)
    last_active: datetime = field(default_factory=datetime.utcnow)


class SessionStore:
    _TTL = timedelta(hours=24)

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
        s = self.get(phone)
        if msg_id in s.processed_ids:
            return True
        s.processed_ids.add(msg_id)
        if len(s.processed_ids) > 500:
            s.processed_ids = set(list(s.processed_ids)[-100:])
        return False

    def _evict(self) -> None:
        cutoff = datetime.utcnow() - self._TTL
        self._store = {k: v for k, v in self._store.items() if v.last_active >= cutoff}


store = SessionStore()
