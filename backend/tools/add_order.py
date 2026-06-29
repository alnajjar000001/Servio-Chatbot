import httpx
from datetime import datetime, timezone, timedelta
from config import settings

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "add_cash_call_order",
        "description": (
            "Create a new cash call maintenance order for the verified customer. "
            "Always call get_order_problems first (silently, without showing the raw list to the user), "
            "then match the customer's reported issue to the closest problemId from that list. "
            "Do NOT ask the user for customerId, locationId, or timestamps — these are injected automatically."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "problem_id": {
                    "type": "integer",
                    "description": "Problem type ID chosen by the customer from the get_order_problems list",
                },
                "general_note": {
                    "type": "string",
                    "description": "Description of the maintenance issue as provided by the customer",
                },
                "priority_id": {
                    "type": "integer",
                    "description": "Priority: 1=Low, 2=Medium (default), 3=High",
                    "enum": [1, 2, 3],
                },
            },
            "required": ["problem_id", "general_note"],
        },
    },
}


def _iso_ms(dt: datetime) -> str:
    """Format datetime as ISO 8601 with milliseconds and Z suffix."""
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def _rfc_date(dt: datetime) -> str:
    """Format datetime as RFC 7231 HTTP date string (GMT)."""
    return dt.strftime("%a, %d %b %Y %H:%M:%S GMT")


async def execute_add_cash_call_order(
    problem_id: int,
    general_note: str,
    priority_id: int = 2,
    # Injected by orchestrator from session context — never passed by the AI
    customer_id: str = "",
    customer_name: str = "",
    location_id: str = "0",
    **kwargs,
) -> dict:
    url = f"{settings.servio_api_base_url}/orderNew/AddOrder?culture=en"

    now_utc = datetime.now(timezone.utc)
    end_utc = now_utc + timedelta(hours=1)

    # Safe location_id coercion
    loc_int = int(location_id) if str(location_id).isdigit() else 0

    payload = {
        "name": customer_name,
        "customerId": customer_id,
        "typeId": 6,          # Cash Call type
        "divisionId": 1,
        "problemId": problem_id,
        "priorityId": priority_id,
        "teamId": 0,
        "startDate": _iso_ms(now_utc),
        "endDate": _iso_ms(end_utc),
        "generalNote": general_note,
        "locationId": loc_int,
        "startDateAsString": _rfc_date(now_utc),
        "endDateAsString": _rfc_date(end_utc),
        "clientTimeOffsetToAdd": -3,   # Kuwait UTC+3
    }

    headers: dict[str, str] = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if settings.servio_api_token:
        headers["Authorization"] = f"Bearer {settings.servio_api_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
