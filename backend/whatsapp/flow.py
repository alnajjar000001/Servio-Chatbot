"""
Menu-driven WhatsApp conversation flow — no OpenAI involved.
Bilingual: English and Arabic, selected by the user on first contact.
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

from whatsapp.i18n import t
from whatsapp.sender import send_text, send_buttons, send_list
from whatsapp.session_store import WASession, FlowState, store

log = logging.getLogger(__name__)

# ── Arabic / English escape words that always reset to main menu ──────────────
_ESCAPE_EN = {"main_menu", "back", "menu", "hi", "hello", "start"}
_ESCAPE_AR = {"مرحبا", "مرحباً", "اهلا", "أهلا", "قائمة", "رئيسية"}


# ── API response helpers ──────────────────────────────────────────────────────

def _list_from(result) -> list:
    """
    Extract a list from any Servio API response shape:
      plain list         →  [...]
      single-wrapped     →  {"data": [...]}
      double-wrapped     →  {"data": {"data": [...]}}   (paginated search)
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
    if isinstance(result, list):
        return bool(result)
    if isinstance(result, dict):
        flag = result.get("isSucceeded")
        if flag is not None:
            return bool(flag)
        return bool(_list_from(result))
    return False


def _gov_id(obj: dict) -> str:
    """Extract governorate ID from an API response object."""
    return str(
        obj.get("id") or obj.get("governorateId") or obj.get("govId") or
        obj.get("GovId") or obj.get("Id") or ""
    )


def _area_id(obj: dict) -> str:
    """Extract area ID from an API response object."""
    return str(
        obj.get("id") or obj.get("areaId") or obj.get("AreaId") or
        obj.get("Id") or ""
    )


def _item_name(obj: dict, *keys: str) -> str:
    for k in keys:
        v = obj.get(k)
        if v:
            return str(v)
    return ""


# ── Paginated WhatsApp list picker ──────────────────────────────────────────────
# WhatsApp interactive list messages cap out at 10 rows TOTAL across all sections,
# so any cached list longer than that has to be paged through with nav rows.

_PAGE_SIZE = 8   # + up to 2 nav rows ("prev"/"more") never exceeds the 10-row cap


def _page_rows(items: list[dict], page: int, id_prefix: str, label_fn, lang: str) -> list[dict]:
    start = page * _PAGE_SIZE
    chunk = items[start:start + _PAGE_SIZE]
    rows = [
        {"id": f"{id_prefix}_{start + i}", "title": label_fn(it, start + i)}
        for i, it in enumerate(chunk)
    ]
    if page > 0:
        rows.insert(0, {"id": f"{id_prefix}_prev", "title": t(lang, "prev_page")})
    if start + _PAGE_SIZE < len(items):
        rows.append({"id": f"{id_prefix}_more", "title": t(lang, "more_options")})
    return rows


def _primary_location_id(data: dict) -> str:
    locations = data.get("locations") or []
    if locations:
        primary = next((l for l in locations if l.get("isPrimary")), locations[0])
        return str(primary.get("id") or primary.get("locationId") or "")
    return str(data.get("locationId") or data.get("defaultLocationId") or "")


def _detect_lang(text: str) -> str | None:
    """Return 'ar', 'en', or None if the language cannot be determined."""
    arabic = sum(1 for c in text if "؀" <= c <= "ۿ")
    latin  = sum(1 for c in text.lower() if "a" <= c <= "z")
    if arabic > latin:
        return "ar"
    if latin > arabic:
        return "en"
    return None


# ── Entry point ───────────────────────────────────────────────────────────────

async def handle(sender: str, text: str, interactive_id: str | None = None) -> None:
    session = store.get(sender)
    inp = (interactive_id or text or "").strip()

    # Auto-detect language from typed text (not from button/list clicks)
    if text and not interactive_id:
        detected = _detect_lang(text)
        if detected:
            session.lang = detected

    # Arabic escape words: switch language and reset
    if inp in _ESCAPE_AR:
        session.lang = "ar"
        await _show_main_menu(sender, session)
        return
    # English escape words: switch language and reset
    if inp.lower() in _ESCAPE_EN:
        session.lang = "en"
        await _show_main_menu(sender, session)
        return

    state = session.state

    if state == FlowState.SELECTING_LANG:
        await _handle_lang_select(sender, inp, session)
    elif state == FlowState.IDLE:
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


# ── Language selection (first-ever contact) ───────────────────────────────────

async def _show_language_select(sender: str, session: WASession) -> None:
    session.state = FlowState.SELECTING_LANG
    await send_buttons(
        sender,
        t("en", "lang_select"),   # always bilingual — user hasn't chosen yet
        [
            {"id": "lang_en", "title": t("en", "btn_lang_en")},
            {"id": "lang_ar", "title": t("en", "btn_lang_ar")},
        ],
    )


async def _handle_lang_select(sender: str, inp: str, session: WASession) -> None:
    if inp == "lang_en":
        session.lang = "en"
    elif inp == "lang_ar":
        session.lang = "ar"
    else:
        # User typed something instead of clicking — detect from text
        detected = _detect_lang(inp)
        if detected:
            session.lang = detected
        # else keep default "en"
    await _show_main_menu(sender, session)


# ── Shared menus ──────────────────────────────────────────────────────────────

async def _show_main_menu(sender: str, session: WASession) -> None:
    session.state = FlowState.IDLE
    lang = session.lang
    await send_buttons(
        sender,
        t(lang, "main_menu_body"),
        [
            {"id": "check_account", "title": t(lang, "btn_check")},
            {"id": "new_customer",  "title": t(lang, "btn_new_cust")},
            {"id": "help",          "title": t(lang, "btn_help")},
        ],
    )


async def _show_service_menu(sender: str, session: WASession) -> None:
    lang = session.lang
    name = session.session_context.customer_name or ("Customer" if lang == "en" else "العميل")
    session.state = FlowState.VERIFIED
    await send_list(
        sender,
        t(lang, "service_menu_body", name=name),
        t(lang, "svc_list_btn"),
        [
            {
                "title": t(lang, "svc_section"),
                "rows": [
                    {"id": "my_orders",    "title": t(lang, "svc_orders"),    "description": t(lang, "svc_orders_desc")},
                    {"id": "my_contracts", "title": t(lang, "svc_contracts"), "description": t(lang, "svc_contracts_desc")},
                    {"id": "my_invoices",  "title": t(lang, "svc_invoices"),  "description": t(lang, "svc_invoices_desc")},
                    {"id": "create_order", "title": t(lang, "svc_create"),    "description": t(lang, "svc_create_desc")},
                ],
            },
            {
                "title": t(lang, "svc_nav_section"),
                "rows": [
                    {"id": "main_menu", "title": t(lang, "svc_menu"), "description": t(lang, "svc_menu_desc")},
                ],
            },
        ],
    )


# ── IDLE: main menu selections ────────────────────────────────────────────────

async def _handle_idle(sender: str, inp: str, session: WASession) -> None:
    lang = session.lang
    if inp == "check_account":
        session.state = FlowState.AWAITING_PHONE
        await send_text(sender, t(lang, "ask_phone"))
    elif inp == "new_customer":
        session.state = FlowState.REG_NAME
        await send_text(sender, t(lang, "ask_name"))
    elif inp == "help":
        await send_text(sender, t(lang, "help_text"))
    else:
        await _show_main_menu(sender, session)


# ── Customer lookup ───────────────────────────────────────────────────────────

async def _handle_phone(sender: str, text: str, session: WASession) -> None:
    lang = session.lang
    phone = text.strip().replace(" ", "").replace("-", "")
    await send_text(sender, t(lang, "looking_up"))

    result = await execute_search_customer(phoneNumber=phone)
    customers = _list_from(result)

    if not customers or not _succeeded(result):
        await send_buttons(
            sender,
            t(lang, "not_found"),
            [
                {"id": "new_customer",  "title": t(lang, "btn_register")},
                {"id": "check_account", "title": t(lang, "btn_retry")},
                {"id": "main_menu",     "title": t(lang, "btn_main")},
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


# ── Service menu ──────────────────────────────────────────────────────────────

async def _handle_service(sender: str, inp: str, session: WASession) -> None:
    lang = session.lang
    cid  = session.session_context.customer_id

    if inp == "my_orders":
        result = await execute_get_customer_orders(customer_id=cid)
        orders = _list_from(result)
        if not orders:
            await send_text(sender, t(lang, "no_orders"))
        else:
            lines = [t(lang, "orders_header")]
            for o in orders[:5]:
                status    = _item_name(o, "statusName", "status") or "-"
                type_name = _item_name(o, "orderProblem", "typeName", "orderType", "description", "problemName") or "-"
                date      = (_item_name(o, "startDate", "orderDate", "date") or "")[:10]
                lines.append(f"• {type_name} — {status}  ({date})")
            await send_text(sender, "\n".join(lines))
        await _show_service_menu(sender, session)

    elif inp == "my_contracts":
        result = await execute_get_customer_contracts(customer_id=cid)
        contracts = _list_from(result)
        if not contracts:
            await send_text(sender, t(lang, "no_contracts"))
        else:
            lines = [t(lang, "contracts_header")]
            for c in contracts[:5]:
                number = _item_name(c, "contractNumber", "contractName", "number") or "-"
                status = _item_name(c, "contractStatus", "statusName", "status") or "-"
                lines.append(t(lang, "contract_line", number=number, status=status))
            await send_text(sender, "\n".join(lines))
        await _show_service_menu(sender, session)

    elif inp == "my_invoices":
        result = await execute_get_contract_invoices(customer_id=cid)
        invoices = _list_from(result)
        if not invoices:
            await send_text(sender, t(lang, "no_invoices"))
        else:
            lines = [t(lang, "invoices_header")]
            for inv in invoices[:5]:
                num    = _item_name(inv, "invoiceNumber", "number") or "-"
                amount = _item_name(inv, "amount", "total", "totalAmount") or "-"
                status = _item_name(inv, "status", "invoiceStatus", "statusName") or "-"
                lines.append(f"• #{num}  {amount} KWD — {status}")
            await send_text(sender, "\n".join(lines))
        await _show_service_menu(sender, session)

    elif inp == "create_order":
        await _start_order_flow(sender, session)

    else:
        await _show_service_menu(sender, session)


# ── Service request: problem → description → confirm ─────────────────────────

async def _start_order_flow(sender: str, session: WASession) -> None:
    lang = session.lang
    await send_text(sender, t(lang, "loading_problems"))

    result   = await execute_get_order_problems()
    problems = _list_from(result)

    if not problems:
        await send_text(sender, t(lang, "no_problems"))
        await _show_service_menu(sender, session)
        return

    # Cache full objects so _handle_problem_selection can get the correct ID
    session.problem_cache = problems
    session.problem_page  = 0
    session.state = FlowState.SELECTING_PROBLEM
    await _send_problem_page(sender, session)


async def _send_problem_page(sender: str, session: WASession) -> None:
    lang = session.lang
    rows = _page_rows(
        session.problem_cache, session.problem_page, "prob",
        lambda p, i: _item_name(p, "name", "problemName", "nameAr") or f"Problem {i + 1}",
        lang,
    )
    await send_list(sender, t(lang, "select_problem"), t(lang, "select_prob_btn"),
                     [{"title": t(lang, "problem_section"), "rows": rows}])


async def _handle_problem_selection(sender: str, inp: str, session: WASession) -> None:
    lang = session.lang
    if inp == "prob_more":
        session.problem_page += 1
        await _send_problem_page(sender, session)
        return
    if inp == "prob_prev":
        session.problem_page = max(0, session.problem_page - 1)
        await _send_problem_page(sender, session)
        return
    if not inp.startswith("prob_"):
        await send_text(sender, t(lang, "invalid_prob"))
        await _send_problem_page(sender, session)
        return

    try:
        idx  = int(inp[5:])
        prob = session.problem_cache[idx]
    except (ValueError, IndexError):
        await send_text(sender, t(lang, "invalid_prob"))
        await _send_problem_page(sender, session)
        return

    session.pending_problem_id = int(prob.get("id") or prob.get("problemId") or 1)
    session.state = FlowState.DESCRIBING_PROBLEM
    await send_text(sender, t(lang, "ask_description"))


async def _handle_problem_description(sender: str, text: str, session: WASession) -> None:
    lang = session.lang
    session.pending_description = text.strip()
    session.state = FlowState.CONFIRMING_ORDER
    await send_buttons(
        sender,
        t(lang, "order_summary", desc=session.pending_description),
        [
            {"id": "confirm_order", "title": t(lang, "btn_yes_submit")},
            {"id": "cancel_order",  "title": t(lang, "btn_cancel")},
        ],
    )


async def _handle_order_confirm(sender: str, inp: str, session: WASession) -> None:
    lang = session.lang
    if inp == "confirm_order":
        ctx = session.session_context
        await send_text(sender, t(lang, "submitting"))
        result = await execute_add_cash_call_order(
            problem_id=session.pending_problem_id or 1,
            general_note=session.pending_description or "-",
            priority_id=2,
            customer_id=ctx.customer_id,
            customer_name=ctx.customer_name,
            location_id=ctx.primary_location_id or "0",
        )
        if _succeeded(result):
            await send_text(sender, t(lang, "order_success"))
        else:
            err = result.get("message") or result.get("error") or "Unknown error"
            await send_text(sender, t(lang, "order_fail", err=err))
    else:
        await send_text(sender, t(lang, "order_cancelled"))

    session.pending_problem_id  = 0
    session.pending_description = ""
    session.problem_cache       = []
    session.problem_page        = 0
    await _show_service_menu(sender, session)


# ── Registration flow ─────────────────────────────────────────────────────────

async def _handle_reg_name(sender: str, text: str, session: WASession) -> None:
    session.reg.name = text.strip()
    session.state    = FlowState.REG_PHONE
    await send_text(sender, t(session.lang, "ask_phone_reg", name=session.reg.name))


async def _handle_reg_phone(sender: str, text: str, session: WASession) -> None:
    session.reg.phone = text.strip().replace(" ", "").replace("-", "")
    await send_text(sender, t(session.lang, "loading_govs"))
    await _send_gov_list(sender, session)


async def _send_gov_list(sender: str, session: WASession) -> None:
    lang   = session.lang
    result = await execute_get_governorates()
    govs   = _list_from(result)

    if not govs:
        await send_text(sender, t(lang, "no_govs"))
        await _show_main_menu(sender, session)
        return

    # Cache the full objects — button ID is just the index
    session.gov_cache = govs
    rows = [
        {
            "id":    f"gov_{i}",
            "title": _item_name(g, "name", "governorateName", "nameAr") or f"Gov {i + 1}",
        }
        for i, g in enumerate(govs[:10])
    ]
    session.state = FlowState.REG_GOV
    await send_list(sender, t(lang, "select_gov"), t(lang, "gov_btn"),
                    [{"title": t(lang, "gov_section"), "rows": rows}])


async def _handle_reg_gov(sender: str, inp: str, session: WASession) -> None:
    lang = session.lang
    if not inp.startswith("gov_"):
        await send_text(sender, t(lang, "invalid_gov"))
        await _send_gov_list(sender, session)
        return

    try:
        idx = int(inp[4:])
        gov = session.gov_cache[idx]
    except (ValueError, IndexError):
        await send_text(sender, t(lang, "invalid_gov"))
        await _send_gov_list(sender, session)
        return

    # Extract actual API ID from the cached object
    gov_id_val = _gov_id(gov)
    if not gov_id_val:
        await send_text(sender, t(lang, "invalid_gov"))
        await _send_gov_list(sender, session)
        return

    session.reg.gov_id = gov_id_val
    await send_text(sender, t(lang, "loading_areas"))

    result = await execute_get_areas_by_governorate(governorate_id=gov_id_val)
    areas  = _list_from(result)

    if not areas:
        await send_text(sender, t(lang, "no_areas"))
        await _send_gov_list(sender, session)
        return

    # Cache the full area objects so _handle_reg_area can get the correct ID
    session.area_cache = areas
    session.area_page  = 0
    session.state = FlowState.REG_AREA
    await _send_area_page(sender, session)


async def _send_area_page(sender: str, session: WASession) -> None:
    lang = session.lang
    rows = _page_rows(
        session.area_cache, session.area_page, "area",
        lambda a, i: _item_name(a, "name", "areaName", "nameAr") or f"Area {i + 1}",
        lang,
    )
    await send_list(sender, t(lang, "select_area"), t(lang, "area_btn"),
                     [{"title": t(lang, "area_section"), "rows": rows}])


async def _handle_reg_area(sender: str, inp: str, session: WASession) -> None:
    lang = session.lang
    if inp == "area_more":
        session.area_page += 1
        await _send_area_page(sender, session)
        return
    if inp == "area_prev":
        session.area_page = max(0, session.area_page - 1)
        await _send_area_page(sender, session)
        return
    if not inp.startswith("area_"):
        await send_text(sender, t(lang, "invalid_area_num"))
        await _send_area_page(sender, session)
        return

    try:
        idx  = int(inp[5:])
        area = session.area_cache[idx]
    except (ValueError, IndexError):
        await send_text(sender, t(lang, "invalid_area_num"))
        await _send_area_page(sender, session)
        return

    area_id_val = _area_id(area)
    if not area_id_val:
        await send_text(sender, t(lang, "invalid_area_num"))
        await _send_area_page(sender, session)
        return

    session.reg.area_id = area_id_val
    session.state       = FlowState.REG_BLOCK
    await send_text(sender, t(lang, "ask_block"))


async def _handle_reg_block(sender: str, text: str, session: WASession) -> None:
    session.reg.block = text.strip()
    session.state     = FlowState.REG_STREET
    await send_text(sender, t(session.lang, "ask_street"))


async def _handle_reg_street(sender: str, text: str, session: WASession) -> None:
    session.reg.street = text.strip()
    session.state      = FlowState.REG_CONFIRM
    lang = session.lang
    reg  = session.reg
    await send_buttons(
        sender,
        t(lang, "reg_summary", name=reg.name, phone=reg.phone, block=reg.block, street=reg.street),
        [
            {"id": "confirm_reg", "title": t(lang, "btn_confirm")},
            {"id": "cancel_reg",  "title": t(lang, "btn_cancel_reg")},
        ],
    )


async def _handle_reg_confirm(sender: str, inp: str, session: WASession) -> None:
    lang = session.lang
    if inp != "confirm_reg":
        await send_text(sender, t(lang, "order_cancelled"))
        await _show_main_menu(sender, session)
        return

    reg = session.reg
    await send_text(sender, t(lang, "registering"))

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
        await send_text(sender, t(lang, "reg_fail", err=err))
        session.state = FlowState.IDLE
        return

    # Auto-verify: look up the new customer
    lookup    = await execute_search_customer(phoneNumber=reg.phone)
    customers = _list_from(lookup)
    if customers:
        data = customers[0]
        session.session_context.customer_id         = str(data.get("id") or data.get("customerId") or "")
        session.session_context.customer_name       = str(data.get("name") or data.get("customerName") or reg.name)
        session.session_context.primary_location_id = _primary_location_id(data)
        session.session_context.customer_phone      = reg.phone
    else:
        session.session_context.customer_name = reg.name

    display_name = session.session_context.customer_name or reg.name
    await send_text(sender, t(lang, "reg_success", name=display_name))
    await _show_service_menu(sender, session)
