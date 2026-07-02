import openai
import json
from typing import Optional

from config import settings
from tools.registry import TOOL_DEFINITIONS, execute_tool
from models.schemas import ChatMessage, SessionContext, ToolCallInfo

client = openai.AsyncOpenAI(api_key=settings.openai_api_key)

SYSTEM_PROMPT = """# Role and Persona
You are "Servio AI", the highly professional, empathetic, and expert virtual assistant for the Servio Property & Maintenance Management platform. Your goal is to guide customers through identity lookup, contract checking, order/invoice retrieval, and creating cash call maintenance requests.

# Conversational Protocol
- Respond natively in the user's preferred language: English or Kuwaiti/Gulf Arabic, matching whichever language the user writes in.
- Keep communication direct, polite, clear, and reassuring.
- NEVER display raw tool JSON inputs or outputs directly to the user. Always translate data into natural, friendly full sentences (e.g. "I found your active contract #1948 for the PIFSS Granada Branch, valid until October 2027.").

# Available Tools
- search_customer — look up a customer by phone number, customer code, or name
- get_customer_contracts — fetch all contracts for the verified customer
- get_customer_orders — fetch all maintenance orders
- get_contract_invoices — fetch all invoices
- get_order_problems — retrieve problem-type master list (call silently, never show raw list)
- add_cash_call_order — create a new cash call maintenance order
- get_governorates — fetch all governorates (for new customer registration)
- get_areas_by_governorate — fetch areas for a selected governorate
- add_customer — register a brand-new customer in the system

# Operational Logic & Rule Constraints

## 1. Identity Verification Phase
- If the user requests contracts, orders, invoices, or wants to file a complaint, check whether `customerId` is present in your session context.
- If `customerId` is missing, politely ask for their mobile phone number or customer code.
- Once provided, immediately invoke `search_customer`.
- From the result, save the `customerId` and `name`, then scan the `locations` array for the object where `isPrimary == true` — use its `id` as the `locationId` for all subsequent operations.
- Greet the verified customer warmly by name and confirm their identity.

## 2. Dynamic Data Retrieval
- When a verified customer asks about contracts, invoices, or orders, immediately call the relevant tool — do not say you "would" do it, just do it.
- After receiving results, summarize naturally. Do not show IDs, dates, or statuses as raw data — narrate them conversationally.

## 3. Creating a New Cash Call Order
- When the user describes a physical problem or complaint (e.g. "My AC broke down", "There is a water leak"), immediately call `get_order_problems` behind the scenes without mentioning it to the user.
- Analyze the problems list and silently match the user's reported issue to the closest `problemId`.
- Map the user's description into the `generalNote` field.
- Use the session's verified `customerId`, `customerName`, matched `problemId`, and primary `locationId` to call `add_cash_call_order`. Never ask the user for these — they are managed automatically.
- Before submitting, briefly confirm the problem type and note with the customer (e.g. "I'll log this as an AC malfunction — shall I go ahead?").

## 4. Registering a New Customer
- If `search_customer` returns no results, immediately offer to register the person as a new customer.
- Collect the following information step-by-step through natural conversation — do NOT ask for everything at once:
  1. **Full name** (if not already provided)
  2. **Phone number** (if not already provided)
  3. **Governorate** — call `get_governorates` silently, then present the names clearly as numbered options (e.g. "1. Capital, 2. Hawalli, 3. Farwaniya…"). Wait for the customer to choose.
  4. **Area** — call `get_areas_by_governorate` with the selected governorateId, then present area names as numbered options. Wait for choice.
  5. **Block** — ask for the block number.
  6. **Street** — ask for the street name or number.
- Before submitting, summarize all collected details and ask for confirmation.
- Call `add_customer` only after confirmation.
- After a successful registration, immediately call `search_customer` using the new phone number to populate the session and greet the newly registered customer by name.

## Strict Validation Gates
- Never attempt data retrieval or order creation without a verified `customerId` in session.
- Never expose internal IDs, tool names, or raw error traces to the user.
- If an API call fails, apologize gracefully and suggest the customer try again or contact the call center."""


# ─── System prompt enriched with verified customer context ────────────────────

def _build_system(ctx: SessionContext) -> str:
    if not ctx.customer_id:
        return SYSTEM_PROMPT
    lines = [
        "\n\n## Active Customer Session — use these values directly in tool calls",
        f"- Customer ID: {ctx.customer_id}",
        f"- Customer Name: {ctx.customer_name}",
        f"- Phone: {ctx.customer_phone}",
    ]
    if ctx.primary_location_id:
        lines.append(f"- Primary Location ID: {ctx.primary_location_id}")
    return SYSTEM_PROMPT + "\n".join(lines)


# ─── Session context injection into tool inputs ───────────────────────────────

_SESSION_TOOLS = {"get_customer_contracts", "get_customer_orders", "get_contract_invoices"}


def _inject_session(tool_name: str, tool_input: dict, ctx: SessionContext) -> dict:
    """Ensure session-derived fields are present before dispatching a tool."""
    if tool_name in _SESSION_TOOLS and ctx.customer_id:
        # Prefer whatever the AI supplied; fall back to session value
        tool_input = {"customer_id": ctx.customer_id, **tool_input}

    if tool_name == "add_cash_call_order":
        tool_input = {
            "customer_id": ctx.customer_id,
            "customer_name": ctx.customer_name,
            "location_id": ctx.primary_location_id or "0",
            **tool_input,   # AI-supplied fields (problem_id, general_note, priority_id) win
        }

    return tool_input


# ─── Result extractors — map raw API payloads to frontend shapes ──────────────

def _items(result: dict) -> list[dict]:
    raw = result.get("data", {})
    if isinstance(raw, dict):
        return raw.get("data", [])
    if isinstance(raw, list):
        return raw
    return []


def _primary_location_id(c: dict, fallback: str = "") -> str:
    """Scan the customer's locations array for isPrimary == true and return its id."""
    locations: list[dict] = c.get("locations") or []
    if locations:
        primary = next((loc for loc in locations if loc.get("isPrimary")), None)
        if primary:
            loc_id = primary.get("id") or primary.get("locationId")
            if loc_id:
                return str(loc_id)
        # Fall back to the first location if none is marked primary
        first_id = locations[0].get("id") or locations[0].get("locationId")
        if first_id:
            return str(first_id)
    # Last resort: top-level scalar fields
    return str(
        c.get("locationId") or c.get("defaultLocationId") or
        c.get("primaryLocationId") or fallback or ""
    )


def _primary_location_obj(c: dict) -> dict:
    """Return the primary location dict for address display in the sidebar."""
    locations: list[dict] = c.get("locations") or []
    if not locations:
        return c   # fall back to top-level fields on the customer object
    return next((loc for loc in locations if loc.get("isPrimary")), locations[0])


def _update_session_from_search(result: dict, ctx: SessionContext) -> SessionContext:
    customers = _items(result)
    if not result.get("isSucceeded") or not customers:
        return ctx
    c = customers[0]
    return SessionContext(
        customer_id=str(c.get("id") or ctx.customer_id or ""),
        customer_name=str(c.get("name") or c.get("customerName") or ctx.customer_name or ""),
        customer_phone=str(c.get("phoneNumber") or c.get("phone") or ctx.customer_phone or ""),
        primary_location_id=_primary_location_id(c, ctx.primary_location_id),
    )


def _extract_customer_display(result: dict) -> Optional[dict]:
    customers = _items(result)
    if not result.get("isSucceeded") or not customers:
        return None
    c = customers[0]
    # Address fields live inside the primary location object when present
    loc = _primary_location_obj(c)
    return {
        "profile": {
            "name": c.get("name") or c.get("customerName") or "",
            "code": c.get("code") or c.get("customerCode") or "",
            "phone": c.get("phoneNumber") or c.get("phone") or "",
            "location": {
                "areaName": loc.get("areaName") or c.get("areaName") or "",
                "governorate": loc.get("governorate") or c.get("governorate") or "",
                "block": loc.get("block") or c.get("block") or "",
                "street": loc.get("street") or c.get("street") or "",
                "building": loc.get("building") or c.get("building") or "",
                "apartment": (
                    loc.get("apartment") or loc.get("appartment") or
                    c.get("apartment") or c.get("appartment") or ""
                ),
            },
        },
        "contracts": [],
        "orders": [],
        "invoices": [],
    }


def _extract_contracts(result: dict) -> list[dict]:
    out = []
    for c in _items(result):
        s = (c.get("contractStatus") or c.get("status") or "").lower()
        status = "expired" if ("expired" in s or "cancel" in s) else "active" if "active" in s else "pending"
        out.append({
            "id": str(c.get("contractNumber") or c.get("id") or ""),
            "title": str(c.get("contractNumber") or c.get("id") or ""),
            "status": status,
            "startDate": (c.get("startDate") or "")[:10],
            "endDate": (c.get("endDate") or "")[:10],
        })
    return out


def _extract_orders(result: dict) -> list[dict]:
    out = []
    for o in _items(result):
        s = (o.get("statusName") or o.get("status") or o.get("orderStatus") or "").lower()
        status = (
            "cancelled" if "cancel" in s else
            "completed" if ("complete" in s or "done" in s or "close" in s) else
            "in-progress" if ("progress" in s or "assigned" in s) else
            "open"
        )
        out.append({
            "id": str(o.get("orderNo") or o.get("orderNumber") or o.get("id") or ""),
            "description": str(
                o.get("orderProblem") or o.get("description") or o.get("problemName") or o.get("name") or ""
            ),
            "status": status,
            "date": (
                o.get("startDate") or o.get("orderDate") or o.get("createdDate") or ""
            )[:10],
        })
    return out


def _extract_invoices(result: dict) -> list[dict]:
    out = []
    for inv in _items(result):
        s = (inv.get("status") or inv.get("invoiceStatus") or "").lower()
        status = (
            "overdue" if ("overdue" in s or "late" in s) else
            "paid" if ("paid" in s and "unpaid" not in s) else
            "unpaid"
        )
        out.append({
            "id": str(inv.get("invoiceNumber") or inv.get("id") or ""),
            "amount": float(inv.get("amount") or inv.get("total") or 0),
            "currency": str(inv.get("currency") or "KWD"),
            "status": status,
            "dueDate": (inv.get("dueDate") or inv.get("invoiceDate") or "")[:10],
        })
    return out


# ─── Main orchestration loop ──────────────────────────────────────────────────

async def run_orchestration(
    user_message: str,
    conversation_history: list[ChatMessage],
    session_context: SessionContext,
) -> tuple[str, list[ToolCallInfo], Optional[dict], SessionContext]:

    messages: list[dict] = [{"role": "system", "content": _build_system(session_context)}]
    for msg in conversation_history:
        messages.append({"role": msg.role.value, "content": msg.content})
    messages.append({"role": "user", "content": user_message})

    tool_calls_made: list[ToolCallInfo] = []
    customer_data: Optional[dict] = None

    response = await client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=settings.max_tokens,
        messages=messages,
        tools=TOOL_DEFINITIONS,
        tool_choice="auto",
    )

    while response.choices[0].finish_reason == "tool_calls":
        assistant_msg = response.choices[0].message

        # Append assistant turn preserving tool_calls metadata
        messages.append(
            {
                "role": "assistant",
                "content": assistant_msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in (assistant_msg.tool_calls or [])
                ],
            }
        )

        for tc in assistant_msg.tool_calls or []:
            tool_input = json.loads(tc.function.arguments)
            tool_input = _inject_session(tc.function.name, tool_input, session_context)

            result = await execute_tool(tc.function.name, tool_input)

            tool_calls_made.append(
                ToolCallInfo(
                    tool_name=tc.function.name,
                    tool_input=tool_input,
                    tool_result=result,
                )
            )

            # ── Side-effects: update session context and customer_data ──────
            if tc.function.name == "search_customer":
                session_context = _update_session_from_search(result, session_context)
                extracted = _extract_customer_display(result)
                if extracted:
                    customer_data = extracted
                    # Re-build system prompt now that we know the customer
                    messages[0] = {"role": "system", "content": _build_system(session_context)}

            elif tc.function.name == "get_customer_contracts":
                contracts = _extract_contracts(result)
                if customer_data is None:
                    # No search in this request; send partial update so frontend merges into existing state
                    customer_data = {"contracts": contracts}
                else:
                    customer_data["contracts"] = contracts

            elif tc.function.name == "get_customer_orders":
                orders = _extract_orders(result)
                if customer_data is None:
                    customer_data = {"orders": orders}
                else:
                    customer_data["orders"] = orders

            elif tc.function.name == "get_contract_invoices":
                invoices = _extract_invoices(result)
                if customer_data is None:
                    customer_data = {"invoices": invoices}
                else:
                    customer_data["invoices"] = invoices

            # Return raw result to the model
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result),
                }
            )

        response = await client.chat.completions.create(
            model=settings.openai_model,
            max_tokens=settings.max_tokens,
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
        )

    final_text = response.choices[0].message.content or ""
    if not final_text.strip():
        final_text = "I encountered an issue processing your request. Please try again."

    return final_text, tool_calls_made, customer_data, session_context
