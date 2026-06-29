from tools.search_customer import TOOL_DEFINITION as T_SEARCH, execute_search_customer
from tools.get_contracts import TOOL_DEFINITION as T_CONTRACTS, execute_get_customer_contracts
from tools.get_orders import TOOL_DEFINITION as T_ORDERS, execute_get_customer_orders
from tools.get_invoices import TOOL_DEFINITION as T_INVOICES, execute_get_contract_invoices
from tools.get_problems import TOOL_DEFINITION as T_PROBLEMS, execute_get_order_problems
from tools.add_order import TOOL_DEFINITION as T_ADD_ORDER, execute_add_cash_call_order

TOOL_DEFINITIONS = [
    T_SEARCH,
    T_CONTRACTS,
    T_ORDERS,
    T_INVOICES,
    T_PROBLEMS,
    T_ADD_ORDER,
]

TOOL_HANDLERS: dict = {
    "search_customer": execute_search_customer,
    "get_customer_contracts": execute_get_customer_contracts,
    "get_customer_orders": execute_get_customer_orders,
    "get_contract_invoices": execute_get_contract_invoices,
    "get_order_problems": execute_get_order_problems,
    "add_cash_call_order": execute_add_cash_call_order,
}


async def execute_tool(tool_name: str, tool_input: dict) -> dict:
    handler = TOOL_HANDLERS.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}", "isSucceeded": False}
    try:
        return await handler(**tool_input)
    except Exception as exc:
        return {"error": str(exc), "isSucceeded": False}
