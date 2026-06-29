import httpx
from config import settings

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_order_problems",
        "description": (
            "Retrieve the master list of problem types for maintenance orders. "
            "Call this silently in the background when the user describes a physical issue — "
            "do NOT present the raw list to the user. Use it to match the closest problemId "
            "before calling add_cash_call_order."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


async def execute_get_order_problems(**kwargs) -> dict:
    url = f"{settings.servio_api_base_url}/OrderProblem/GetAll?culture=en"
    headers: dict[str, str] = {"Accept": "application/json"}
    if settings.servio_api_token:
        headers["Authorization"] = f"Bearer {settings.servio_api_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
