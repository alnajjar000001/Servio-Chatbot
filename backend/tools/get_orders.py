import httpx
from config import settings

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_customer_orders",
        "description": (
            "Retrieve all maintenance orders for the verified customer. "
            "Do NOT ask the user for their customerId — it is injected from the session."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "customer_id": {
                    "type": "string",
                    "description": "Numeric customer ID (from session, injected automatically)",
                }
            },
            "required": ["customer_id"],
        },
    },
}


async def execute_get_customer_orders(customer_id: str, **kwargs) -> dict:
    url = f"{settings.servio_api_base_url}/Customer/GetOrdersOfCutomer/{customer_id}?culture=en"
    headers: dict[str, str] = {"Accept": "application/json"}
    if settings.servio_api_token:
        headers["Authorization"] = f"Bearer {settings.servio_api_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()
