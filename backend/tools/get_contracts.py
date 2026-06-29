import httpx
from config import settings

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "get_customer_contracts",
        "description": (
            "Retrieve all contracts for the verified customer. "
            "Call after identity is confirmed. Do NOT ask the user for their customerId — "
            "it is already in the session."
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


async def execute_get_customer_contracts(customer_id: str, **kwargs) -> dict:
    url = f"{settings.servio_api_base_url}/Customer/GetAllContractsOfCutomer/?culture=en"
    payload = {
        "CustomerId": customer_id,
        "pagingparametermodel": {"pageNo": 1, "pageSize": 20},
    }
    headers: dict[str, str] = {"Content-Type": "application/json", "Accept": "application/json"}
    if settings.servio_api_token:
        headers["Authorization"] = f"Bearer {settings.servio_api_token}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()
