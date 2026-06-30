import httpx
from config import settings

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_areas_by_governorate",
        "description": (
            "Retrieve areas/neighborhoods for a specific governorate. "
            "Call this after the customer selects their governorate during registration, "
            "then present the area options conversationally."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "governorate_id": {
                    "type": "string",
                    "description": "Governorate ID obtained from get_governorates",
                }
            },
            "required": ["governorate_id"],
        },
    },
}


async def execute_get_areas_by_governorate(governorate_id: str, **kwargs) -> dict:
    url = (
        f"{settings.servio_api_base_url}/Areas/GetAreasByGovId"
        f"?GovId={governorate_id}&culture=en"
    )
    headers: dict[str, str] = {"Accept": "application/json"}
    if settings.servio_api_token:
        headers["Authorization"] = f"Bearer {settings.servio_api_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
