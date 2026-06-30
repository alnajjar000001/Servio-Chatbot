import httpx
from config import settings

TOOL_DEFINITION = {
    "type": "function",
    "function": {
        "name": "add_customer",
        "description": (
            "Register a new customer in the Servio system. "
            "Only call after collecting ALL required information from the user: "
            "name, phone, governorateId, areaId, block, and street. "
            "Always confirm the details with the customer before submitting."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Customer's full name",
                },
                "phone": {
                    "type": "string",
                    "description": "Customer's phone number (digits only, e.g. 96555814102)",
                },
                "governorate_id": {
                    "type": "string",
                    "description": "Governorate ID from get_governorates",
                },
                "area_id": {
                    "type": "string",
                    "description": "Area ID from get_areas_by_governorate",
                },
                "block": {
                    "type": "string",
                    "description": "Block number or name",
                },
                "street": {
                    "type": "string",
                    "description": "Street name or number",
                },
            },
            "required": ["name", "phone", "governorate_id", "area_id", "block", "street"],
        },
    },
}


async def execute_add_customer(
    name: str,
    phone: str,
    governorate_id: str,
    area_id: str,
    block: str,
    street: str,
    **kwargs,
) -> dict:
    url = f"{settings.servio_api_base_url}/customer/AddCustomerFromWeb?culture=en"

    payload = {
        "name": name,
        "customerPhoneBook": [
            {
                "phoneTypeId": 2,   # fixed: mobile
                "isNew": True,
                "isPrimary": True,
                "phone": phone,
                "isExist": False,
            }
        ],
        "locations": [
            {
                "governorateId": governorate_id,
                "areaId": area_id,
                "block": block,
                "street": street,
                "isValid": True,
                "isPrimary": True,
            }
        ],
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
