import httpx
from config import settings

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_governorates",
        "description": (
            "Retrieve the list of all governorates available in the Servio system. "
            "Call this silently when registering a new customer so you can present "
            "governorate options conversationally — do NOT dump the raw list."
        ),
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
}


async def execute_get_governorates(**kwargs) -> dict:
    url = f"{settings.servio_api_base_url}/Governorates/GetAllWithBlocked?culture=en"
    headers: dict[str, str] = {"Accept": "application/json"}
    if settings.servio_api_token:
        headers["Authorization"] = f"Bearer {settings.servio_api_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
