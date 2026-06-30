"""
Menu-driven WhatsApp conversation flow — no OpenAI involved.
Calls Servio API tools directly and replies with interactive messages.
"""

import logging

from tools.search_customer import execute_search_customer
from tools.get_contracts import execute_get_customer_contracts
from tools.get_orders import execute_get_customer_orders
from tools.get_invoices import execute_get_contract_invoices
from tools.add_order import execute_add_cash_call_order
from tools.get_governorates import execute_get_governorates
from tools.get_areas import execute_get_areas_by_governorate
from tools.add_customer import execute_add_customer
from tools.get_problems import execute_get_order_problems

from whatsapp.sender import send_text, send_buttons, send_list
from whatsapp.session_store import WASession, FlowState, store

log = logging.getLogger(__name__)


# ── Response helpers ──────────────────────────────────────────────────────────

def _list_from(result) -> list:
    """
    Safely extract a list from any Servio API response shape:
      - plain list:              [...]
      - single-wrapped:          {"data": [...]}
      - double-wrapped (paging): {"data": {"data": [...]}}
    """
    if isinstance(result, list):
        return result
    if not isinstance(result, dict):
        return []
    raw = result.get("data")
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        inner = raw.get("data")
        if isinstance(inner, list):
            return inner
    return []


def _succeeded(result) -> bool:
    """True when the API call reports success (or when result is a non-empty list)."""
    if isinstance(result, list):
        return bool(result)
    if isinstance(result, dict):
        flag = result.get("isSucceeded")
        if flag is not None:
            return bool(flag)
        # Fall back: consider success if a data list is present
        return bool(_list_from(result))
    return False


def _primary_location_id(data: dict) -> str:
    locations = data.get("locations") or []
    if locations:
        primary = next((l for l in locations if l.get("isPrimary")), locations[0])
        return str(primary.get("id") or primary.get("locationId") or "")
    return str(data.get("locationId") or data.get("defaultLocationId") or "")


# ── Entry point ───────────────────────────────────────────────────────────────

async def handle(sender: str, text: str, interactive_id: str | None = None) -> None:
    """
    Route incoming message to the correct state handler.
    `interactive_id` is set when the user tapped a button or list row.
    """
    session = store.get(sender)
    inp = (interactive_id or text or "").strip()

    # Global escape: reset to main menu
    if inp.lower() in ("main_menu", "back", "menu", "hi", "hello", "start",
                       "مرحبا", "اهلا", "مرحبا بك"):
        await _show_main_menu(sender, session)
        return

    state = session.state

    if state == FlowState.IDLE:
        await _handle_idle(sender, inp, session)
    elif state == FlowState.AWAITING_PHONE:
        await _handle_phone(sender, text, session)
    elif state == FlowState.VERIFIED:
        await _handle_service(sender, inp, session)
    elif state == FlowState.SELECTING_PROBLEM:
        await _handle_problem_selection(sender, inp, session)
    elif state == FlowState.DESCRIBING_PROBLEM:
        await _handle_problem_description(sender, text, session)
    elif state == FlowState.CONFIRMING_ORDER:
        await _handle_order_confirm(sender, inp, session)
    elif state == FlowState.REG_NAME:
        await _handle_reg_name(sender, text, session)
    elif state == FlowState.REG_PHONE:
        await _handle_reg_phone(sender, text, session)
    elif state == FlowState.REG_GOV:
        await _handle_reg_gov(sender, inp, session)
    elif state == FlowState.REG_AREA:
        await _handle_reg_area(sender, inp, session)
    elif state == FlowState.REG_BLOCK:
        await _handle_reg_block(sender, text, session)
    elif state == FlowState.REG_STREET:
        await _handle_reg_street(sender, text, session)
    elif state == FlowState.REG_CONFIRM:
        await _handle_reg_confirm(sender, inp, session)
    else:
        await _show_main_menu(sender, session)


# ── Shared menus ──────────────────────────────────────────────────────────────

async def _show_main_menu(sender: str, session: WASession) -> None:
    session.state = FlowState.IDLE
    await send_buttons(
        sender,
        "👋 Welcome to *Servio AI*!\n\nHow can I help you today?",
        [
            {"id": "check_account", "title": "Check Account"},
            {"id": "new_customer",  "title": "New Customer"},
            {"id": "help",          "title": "Help & Support"},
        ],
    )


async def _show_service_menu(sender: str, session: WASession) -> None:
    name = session.session_context.customer_name or "Customer"
    session.state = FlowState.VERIFIED
    await send_list(
        sender,
        f"Hello *{name}*! ✅\n\nWhat would you like to do?",
        "Select Option",
        [
            {
                "title": "My Account",
                "rows": [
                    {"id": "my_orders",    "title": "My Orders",
                     "description": "View your recent orders"},
                    {"id": "my_contracts", "title": "My Contracts",
                     "description": "View active contracts"},
                    {"id": "my_invoices",  "title": "My Invoices",
                     "description": "View your invoices"},
                    {"id": "create_order", "title": "Create Service Request",
                     "description": "Schedule a cash call visit"},
                ],
            },
            {
                "title": "Navigation",
                "rows": [
                    {"id": "main_menu", "title": "Main Menu",
                     "description": "Return to main menu"},
                ],
            },
        ],
    )


# ── IDLE: main menu button selections ─────────────────────────────────────────

async def _handle_idle(sender: str, inp: str, session: WASession) -> None:
    if inp == "check_account":
        session.state = FlowState.AWAITING_PHONE
        await send_text(sender, "Please enter your registered phone number:")
    elif inp == "new_customer":
        session.state = FlowState.REG_NAME
        await send_text(sender, "Let's get you registered! 📋\n\nPlease enter your *full name*:")
    elif inp == "help":
        await send_text(
            sender,
            "📞 *Servio Support*\n\n"
            "For assistance please contact our call center.\n\n"
            "Type *hi* or *menu* to return to the main menu."
        )
    else:
        await _show_main_menu(sender, session)


# ── Customer lookup ───────────────────────────────────────────────────────────

async def _handle_phone(sender: str, text: str, session: WASession) -> None:
    phone = text.strip().replace(" ", "").replace("-", "")
    await send_text(sender, "🔍 Looking up your account...")

    result = await execute_search_customer(phoneNumber=phone)

    if not _succeeded(result):
        await send_buttons(
            sender,
            "❌ No account found for that number.\n\nWould you like to register as a new customer?",
            [
                {"id": "new_customer",  "title": "Register Now"},
                {"id": "check_account", "title": "Try Again"},
                {"id": "main_menu",     "title": "Main Menu"},
            ],
        )
        session.state = FlowState.IDLE
        return

    customers = _list_from(result)
    if not customers:
        await send_buttons(
            sender,
            "❌ No account found for that number.\n\nWould you like to register as a new customer?",
            [
                {"id": "new_customer",  "title": "Register Now"},
                {"id": "check_account", "title": "Try Again"},
                {"id": "main_menu",     "title": "Main Menu"},
            ],
        )
        session.state = FlowState.IDLE
        return

    data = customers[0]
    session.session_context.customer_id         = str(data.get("id") or data.get("customerId") or "")
    session.session_context.customer_name       = str(data.get("name") or data.get("customerName") or "")
    session.session_context.primary_location_id = _primary_location_id(data)
    session.session_context.customer_phone      = phone

    await _show_service_menu(sender, session)


# ── Service menu actions ──────────────────────────────────────────────────────

async def _handle_service(sender: str, inp: str, session: WASession) -> None:
    cid = session.session_context.customer_id

    if inp == "my_orders":
        result = await execute_get_customer_orders(customer_id=cid)
        orders = _list_from(result)
        if not orders:
            await send_text(sender, "📦 No orders found for your account.")
        else:
            lines = ["📦 *Your Recent Orders:*\n"]
            for o in orders[:5]:
                status    = o.get("statusName")    or o.get("status")    or "-"
                type_name = o.get("typeName")      or o.get("orderType") or o.get("description") or "-"
                date      = (o.get("startDate")    or o.get("orderDate") or o.get("date") or "")[:10]
                lines.append(f"• {type_name} — {status}  ({date})")
            await send_text(sender, "\n".join(lines))
        await _show_service_menu(sender, session)

    elif inp == "my_contracts":
        result = await execute_get_customer_contracts(customer_id=cid)
        contracts = _list_from(result)
        if not contracts:
            await send_text(sender, "📄 No contracts found for your account.")
        else:
            lines = ["📄 *Your Contracts:*\n"]
            for c in contracts[:5]:
                name   = c.get("contractName") or c.get("customer") or c.get("name")       or "-"
                status = c.get("contractStatus") or c.get("statusName") or c.get("status") or "-"
                lines.append(f"• {name} — {status}")
            await send_text(sender, "\n".join(lines))
        await _show_service_menu(sender, session)

    elif inp == "my_invoices":
        result = await execute_get_contract_invoices(customer_id=cid)
        invoices = _list_from(result)
        if not invoices:
            await send_text(sender, "🧾 No invoices found for your account.")
        else:
            lines = ["🧾 *Your Invoices:*\n"]
            for inv in invoices[:5]:
                num    = inv.get("invoiceNumber") or inv.get("number")                or "-"
                amount = inv.get("amount")        or inv.get("total") or inv.get("totalAmount") or "-"
                status = inv.get("status")        or inv.get("invoiceStatus") or inv.get("statusName") or "-"
                lines.append(f"• #{num}  {amount} KWD — {status}")
            await send_text(sender, "\n".join(lines))
        await _show_service_menu(sender, session)

    elif inp == "create_order":
        await _start_order_flow(sender, session)

    else:
        await _show_service_menu(sender, session)


# ── Service request: problem → description → confirm ─────────────────────────

async def _start_order_flow(sender: str, session: WASession) -> None:
    await send_text(sender, "🔍 Loading problem types...")
    result = await execute_get_order_problems()
    problems = _list_from(result)

    if not problems:
        await send_text(sender, "❌ Could not load problem types. Please try again later.")
        await _show_service_menu(sender, session)
        return

    all_rows = [
        {
            "id":    f"prob_{p.get('id') or p.get('problemId') or i}",
            "title": (p.get("name") or p.get("problemName") or f"Problem {i + 1}")[:24],
        }
        for i, p in enumerate(problems[:20])
    ]

    sections = [{"title": "Problem Types", "rows": all_rows[:10]}]
    if len(all_rows) > 10:
        sections.append({"title": "More Types", "rows": all_rows[10:20]})

    session.state = FlowState.SELECTING_PROBLEM
    await send_list(
        sender,
        "🔧 *Create Service Request*\n\nPlease select the type of issue:",
        "Select Problem",
        sections,
    )


async def _handle_problem_selection(sender: str, inp: str, session: WASession) -> None:
    if not inp.startswith("prob_"):
        await send_text(sender, "Please select a problem type from the list.")
        await _start_order_flow(sender, session)
        return

    raw_id = inp[5:]   # strip "prob_"
    try:
        session.pending_problem_id = int(raw_id)
    except ValueError:
        session.pending_problem_id = 0

    # We don't know the name easily here; store the id and move on
    session.state = FlowState.DESCRIBING_PROBLEM
    await send_text(sender, "Please describe the issue briefly\n(e.g. *AC not working*, *water leak under sink*):")


async def _handle_problem_description(sender: str, text: str, session: WASession) -> None:
    session.pending_description = text.strip()
    session.state = FlowState.CONFIRMING_ORDER
    await send_buttons(
        sender,
        f"🔧 *Service Request Summary*\n\n"
        f"Issue: {session.pending_description}\n\n"
        f"Shall I submit this request for your primary location?",
        [
            {"id": "confirm_order", "title": "Yes, Submit"},
            {"id": "cancel_order",  "title": "Cancel"},
        ],
    )


async def _handle_order_confirm(sender: str, inp: str, session: WASession) -> None:
    if inp == "confirm_order":
        ctx = session.session_context
        await send_text(sender, "⏳ Submitting your service request...")
        result = await execute_add_cash_call_order(
            problem_id=session.pending_problem_id or 1,
            general_note=session.pending_description or "Cash call request",
            priority_id=2,
            customer_id=ctx.customer_id,
            customer_name=ctx.customer_name,
            location_id=ctx.primary_location_id or "0",
        )
        if _succeeded(result):
            await send_text(sender, "✅ Service request submitted!\n\nOur team will contact you shortly.")
        else:
            err = result.get("message") or result.get("error") or "Unknown error"
            await send_text(sender, f"❌ Could not submit the request: {err}")
    else:
        await send_text(sender, "Request cancelled.")

    # Clear pending order data
    session.pending_problem_id   = 0
    session.pending_problem_name = ""
    session.pending_description  = ""
    await _show_service_menu(sender, session)


# ── Registration flow ─────────────────────────────────────────────────────────

async def _handle_reg_name(sender: str, text: str, session: WASession) -> None:
    session.reg.name = text.strip()
    session.state = FlowState.REG_PHONE
    await send_text(sender, f"Great, *{session.reg.name}*! 👍\n\nNow enter your *phone number*:")


async def _handle_reg_phone(sender: str, text: str, session: WASession) -> None:
    session.reg.phone = text.strip().replace(" ", "").replace("-", "")
    await send_text(sender, "📍 Fetching governorates...")
    await _send_gov_list(sender, session)


async def _send_gov_list(sender: str, session: WASession) -> None:
    result = await execute_get_governorates()
    govs = _list_from(result)
    if not govs:
        await send_text(sender, "❌ Could not load governorates. Please try again later.")
        await _show_main_menu(sender, session)
        return

    rows = [
        {
            "id":    f"gov_{g.get('id') or g.get('governorateId') or i}",
            "title": (g.get("name") or g.get("governorateName") or f"Governorate {i + 1}")[:24],
        }
        for i, g in enumerate(govs[:10])
    ]
    session.state = FlowState.REG_GOV
    await send_list(
        sender,
        "Please select your *governorate*:",
        "Choose Governorate",
        [{"title": "Governorates", "rows": rows}],
    )


async def _handle_reg_gov(sender: str, inp: str, session: WASession) -> None:
    if not inp.startswith("gov_"):
        await send_text(sender, "Please select a governorate from the list.")
        await _send_gov_list(sender, session)
        return

    session.reg.gov_id = inp[4:]   # strip "gov_"
    await send_text(sender, "📍 Fetching areas...")

    result = await execute_get_areas_by_governorate(governorate_id=session.reg.gov_id)
    areas = _list_from(result)
    if not areas:
        await send_text(sender, "❌ Could not load areas. Please try again.")
        await _send_gov_list(sender, session)
        return

    all_rows = [
        {
            "id":    f"area_{a.get('id') or a.get('areaId') or i}",
            "title": (a.get("name") or a.get("areaName") or f"Area {i + 1}")[:24],
        }
        for i, a in enumerate(areas[:20])
    ]
    sections = [{"title": "Areas", "rows": all_rows[:10]}]
    if len(all_rows) > 10:
        sections.append({"title": "More Areas", "rows": all_rows[10:20]})

    session.state = FlowState.REG_AREA
    await send_list(
        sender,
        "Please select your *area*:",
        "Choose Area",
        sections,
    )


async def _handle_reg_area(sender: str, inp: str, session: WASession) -> None:
    if not inp.startswith("area_"):
        await send_text(sender, "Please select an area from the list.")
        return
    session.reg.area_id = inp[5:]   # strip "area_"
    session.state = FlowState.REG_BLOCK
    await send_text(sender, "Please enter your *block number*:")


async def _handle_reg_block(sender: str, text: str, session: WASession) -> None:
    session.reg.block = text.strip()
    session.state = FlowState.REG_STREET
    await send_text(sender, "Please enter your *street name or number*:")


async def _handle_reg_street(sender: str, text: str, session: WASession) -> None:
    session.reg.street = text.strip()
    session.state = FlowState.REG_CONFIRM
    reg = session.reg
    await send_buttons(
        sender,
        f"📋 *Registration Summary*\n\n"
        f"Name:   {reg.name}\n"
        f"Phone:  {reg.phone}\n"
        f"Block:  {reg.block}\n"
        f"Street: {reg.street}\n\n"
        f"Confirm to complete registration.",
        [
            {"id": "confirm_reg", "title": "Confirm"},
            {"id": "cancel_reg",  "title": "Cancel"},
        ],
    )


async def _handle_reg_confirm(sender: str, inp: str, session: WASession) -> None:
    if inp != "confirm_reg":
        await send_text(sender, "Registration cancelled.")
        await _show_main_menu(sender, session)
        return

    reg = session.reg
    await send_text(sender, "⏳ Creating your account...")

    result = await execute_add_customer(
        name=reg.name,
        phone=reg.phone,
        governorate_id=reg.gov_id,
        area_id=reg.area_id,
        block=reg.block,
        street=reg.street,
    )

    if not (_succeeded(result) or result.get("id") or result.get("customerId")):
        err = result.get("message") or result.get("error") or "Unknown error"
        await send_text(sender, f"❌ Registration failed: {err}\n\nType *hi* to start over.")
        session.state = FlowState.IDLE
        return

    # Auto-verify: look up the newly registered customer
    lookup = await execute_search_customer(phoneNumber=reg.phone)
    customers = _list_from(lookup)
    if customers:
        data = customers[0]
        session.session_context.customer_id         = str(data.get("id") or data.get("customerId") or "")
        session.session_context.customer_name       = str(data.get("name") or data.get("customerName") or reg.name)
        session.session_context.primary_location_id = _primary_location_id(data)
        session.session_context.customer_phone      = reg.phone
    else:
        session.session_context.customer_name = reg.name

    await send_text(sender, f"✅ Welcome to Servio, *{session.session_context.customer_name}*! Your account has been created.")
    await _show_service_menu(sender, session)
