import httpx
from config import settings

# OpenAI function-calling tool definition format
TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "search_customer",
        "description": (
            "Search for a customer in the Servio system. "
            "Call this whenever the user provides a phone number, customer code, name, "
            "or contract number to look up their account."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "phoneNumber": {
                    "type": "string",
                    "description": "Customer phone number (e.g. 96565986598)",
                },
                "customerCode": {
                    "type": "string",
                    "description": "Customer code (e.g. 0002026083)",
                },
                "name": {
                    "type": "string",
                    "description": "Customer full name or partial name",
                },
                "contractNumber": {
                    "type": "string",
                    "description": "Contract number associated with the customer",
                },
            },
            "required": [],
        },
    },
}


async def execute_search_customer(
    phoneNumber: str = "",
    customerCode: str = "",
    name: str = "",
    contractNumber: str = "",
    address: str = "",
    block: str = "",
    street: str = "",
    appartment: str = "",
    building: str = "",
    **kwargs,
) -> dict:
    url = f"{settings.servio_api_base_url}/customer/SearchCustomerOfCallCenter?culture=en"

    payload = {
        "name": name,
        "phoneNumber": phoneNumber,
        "address": address,
        "cID": "",
        "contractNumber": contractNumber,
        "block": block,
        "street": street,
        "appartment": appartment,
        "building": building,
        "customerCode": customerCode,
        "isExact": "true",
        "isStartWith": "false",
        "typeOfSearchCustomerCode": 2,
        "typeOfSearchName": 2,
        "pagingparametermodel": {"pageNo": 1, "pageSize": 5},
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
