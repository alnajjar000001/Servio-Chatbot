"""Bilingual strings (English / Arabic) for the WhatsApp bot."""

_T: dict[str, dict[str, str]] = {
    "en": {
        # Language selection
        "lang_select": (
            "Welcome to Servio AI 👋\nمرحباً بك في Servio AI 👋\n\n"
            "Please select your language / اختر لغتك:"
        ),
        "btn_lang_en": "English",
        "btn_lang_ar": "العربية",

        # Main menu
        "main_menu_body": "👋 Welcome to *Servio AI*!\n\nHow can I help you today?",
        "btn_check":    "Check Account",
        "btn_new_cust": "New Customer",
        "btn_help":     "Help & Support",

        # Service menu
        "service_menu_body": "Hello *{name}*! ✅\n\nWhat would you like to do?",
        "svc_section":       "My Account",
        "svc_nav_section":   "Navigation",
        "svc_orders":        "My Orders",
        "svc_orders_desc":   "Track your recent service orders",
        "svc_contracts":     "My Contracts",
        "svc_contracts_desc":"View your contracts and their status",
        "svc_invoices":      "My Invoices",
        "svc_invoices_desc": "Check your invoices and balances",
        "svc_create":        "Create Service Request",
        "svc_create_desc":   "Report an issue and request a visit",
        "svc_menu":          "Main Menu",
        "svc_menu_desc":     "Return to the main menu",
        "svc_list_btn":      "Select Option",

        # Phone lookup
        "ask_phone":    "📱 Please enter your registered phone number:",
        "looking_up":   "🔍 Looking up your account...",
        "not_found":    "❌ We couldn't find an account for that number.\n\nWould you like to register as a new customer?",
        "btn_register": "Register Now",
        "btn_retry":    "Try Again",
        "btn_main":     "Main Menu",

        # Account data
        "orders_header":    "📦 *Your Recent Orders:*\n",
        "no_orders":        "📦 You don't have any orders yet.",
        "contracts_header": "📄 *Your Contracts:*\n",
        "no_contracts":     "📄 You don't have any contracts yet.",
        "contract_line":    "• Contract No: {number} — Status: {status}",
        "invoices_header":  "🧾 *Your Invoices:*\n",
        "no_invoices":      "🧾 You don't have any invoices yet.",

        # Service request
        "loading_problems":  "🔍 Loading problem types...",
        "no_problems":       "❌ Couldn't load problem types. Please try again in a moment.",
        "select_problem":    "🔧 *Create Service Request*\n\nWhat type of issue are you experiencing?",
        "problem_section":   "Problem Types",
        "select_prob_btn":   "Select Problem",
        "ask_description":   "📝 Please briefly describe the issue\n(e.g. *AC not working*, *water leak*):",
        "order_summary":     "🔧 *Service Request Summary*\n\n📝 Issue: {desc}\n\nShall I submit this for your registered address?",
        "btn_yes_submit":    "Yes, Submit",
        "btn_cancel":        "Cancel",
        "submitting":        "⏳ Submitting your service request...",
        "order_success":     "✅ Your request has been submitted!\n\nOur team will contact you shortly.",
        "order_fail":        "❌ We couldn't submit your request: {err}\n\nPlease try again, or type *hi* to start over.",
        "order_cancelled":   "Request cancelled. Type *hi* anytime to start over.",

        # Help
        "help_text": (
            "📞 *Servio Support*\n\n"
            "Need a hand? Our call center team is ready to help.\n\n"
            "Type *hi* or *menu* anytime to return to the main menu."
        ),

        # Registration
        "ask_name":       "Let's get you registered! 📋\n\nPlease enter your *full name*:",
        "ask_phone_reg":  "Great, *{name}*! 👍\n\nNow enter your *phone number*:",
        "loading_govs":   "📍 Fetching governorates...",
        "no_govs":        "❌ Couldn't load governorates. Please try again later.",
        "select_gov":     "📍 Please select your *governorate*:",
        "gov_section":    "Governorates",
        "gov_btn":        "Choose Governorate",
        "loading_areas":  "📍 Fetching areas...",
        "no_areas":       "❌ Couldn't load areas. Please try again.",
        "select_area":    "📍 Please select your *area*:",
        "area_section":   "Areas",
        "area_btn":       "Choose Area",
        "invalid_area_num": "Please select an area from the list.",
        "more_options":   "➡️ More Options",
        "prev_page":      "⬅️ Previous",
        "ask_block":      "🧱 Please enter your *block number*:",
        "ask_street":     "🛣️ Please enter your *street name or number*:",
        "reg_summary": (
            "📋 *Registration Summary*\n\n"
            "👤 Name: {name}\n"
            "📱 Phone: {phone}\n"
            "🧱 Block: {block}\n"
            "🛣️ Street: {street}\n\n"
            "Does everything look correct? Confirm to complete your registration."
        ),
        "btn_confirm":    "Confirm",
        "btn_cancel_reg": "Cancel",
        "registering":    "⏳ Creating your account...",
        "reg_fail":       "❌ Registration failed: {err}\n\nPlease try again, or type *hi* to start over.",
        "reg_success":    "✅ Welcome to Servio, *{name}*! Your account has been created.",

        # Errors
        "generic_error": "⚠️ Sorry, something went wrong. Please type *hi* to try again.",
        "invalid_gov":   "Please select a governorate from the list.",
        "invalid_area":  "Please select an area from the list.",
        "invalid_prob":  "Please select a problem type from the list.",
    },

    "ar": {
        # Language selection (same bilingual text)
        "lang_select": (
            "Welcome to Servio AI 👋\nمرحباً بك في Servio AI 👋\n\n"
            "Please select your language / اختر لغتك:"
        ),
        "btn_lang_en": "English",
        "btn_lang_ar": "العربية",

        # Main menu
        "main_menu_body": "👋 أهلاً بك في *Servio AI*!\n\nكيف يمكنني مساعدتك اليوم؟",
        "btn_check":    "حسابي",
        "btn_new_cust": "عميل جديد",
        "btn_help":     "المساعدة",

        # Service menu
        "service_menu_body": "مرحباً *{name}*! ✅\n\nماذا تريد أن تفعل؟",
        "svc_section":       "حسابي",
        "svc_nav_section":   "التنقل",
        "svc_orders":        "طلباتي",
        "svc_orders_desc":   "تتبّع طلبات الصيانة الأخيرة",
        "svc_contracts":     "عقودي",
        "svc_contracts_desc":"عرض عقودك وحالتها",
        "svc_invoices":      "فواتيري",
        "svc_invoices_desc": "متابعة فواتيرك وأرصدتك",
        "svc_create":        "طلب خدمة",
        "svc_create_desc":   "الإبلاغ عن مشكلة وطلب زيارة",
        "svc_menu":          "القائمة الرئيسية",
        "svc_menu_desc":     "العودة للقائمة الرئيسية",
        "svc_list_btn":      "اختر خياراً",

        # Phone lookup
        "ask_phone":    "📱 الرجاء إدخال رقم هاتفك المسجل:",
        "looking_up":   "🔍 جاري البحث عن حسابك...",
        "not_found":    "❌ لم نتمكن من العثور على حساب بهذا الرقم.\n\nهل ترغب بالتسجيل كعميل جديد؟",
        "btn_register": "سجّل الآن",
        "btn_retry":    "حاول مجدداً",
        "btn_main":     "القائمة",

        # Account data
        "orders_header":    "📦 *طلباتك الأخيرة:*\n",
        "no_orders":        "📦 لا توجد طلبات في حسابك بعد.",
        "contracts_header": "📄 *عقودك:*\n",
        "no_contracts":     "📄 لا توجد عقود في حسابك بعد.",
        "contract_line":    "• رقم العقد: {number} — الحالة: {status}",
        "invoices_header":  "🧾 *فواتيرك:*\n",
        "no_invoices":      "🧾 لا توجد فواتير في حسابك بعد.",

        # Service request
        "loading_problems": "🔍 جاري تحميل أنواع المشاكل...",
        "no_problems":      "❌ تعذّر تحميل أنواع المشاكل. حاول بعد قليل.",
        "select_problem":   "🔧 *طلب خدمة جديد*\n\nما نوع المشكلة التي تواجهها؟",
        "problem_section":  "أنواع المشاكل",
        "select_prob_btn":  "اختر المشكلة",
        "ask_description":  "📝 صف المشكلة بإيجاز\n(مثال: *المكيف لا يعمل*، *تسرب مياه*):",
        "order_summary":    "🔧 *ملخص طلب الخدمة*\n\n📝 المشكلة: {desc}\n\nهل أرسل الطلب لعنوانك المسجل؟",
        "btn_yes_submit":   "نعم، أرسل",
        "btn_cancel":       "إلغاء",
        "submitting":       "⏳ جاري إرسال طلبك...",
        "order_success":    "✅ تم إرسال طلبك بنجاح!\n\nسيتواصل معك فريقنا قريباً.",
        "order_fail":       "❌ تعذّر إرسال طلبك: {err}\n\nحاول مجدداً، أو اكتب *مرحبا* للبدء من جديد.",
        "order_cancelled":  "تم إلغاء الطلب. اكتب *مرحبا* في أي وقت للبدء من جديد.",

        # Help
        "help_text": (
            "📞 *دعم Servio*\n\n"
            "هل تحتاج مساعدة؟ فريق مركز الاتصال جاهز لخدمتك.\n\n"
            "اكتب *مرحبا* أو *قائمة* في أي وقت للعودة للقائمة الرئيسية."
        ),

        # Registration
        "ask_name":       "لنقم بتسجيلك! 📋\n\nأدخل *اسمك الكامل*:",
        "ask_phone_reg":  "ممتاز، *{name}*! 👍\n\nأدخل *رقم هاتفك*:",
        "loading_govs":   "📍 جاري تحميل المحافظات...",
        "no_govs":        "❌ تعذّر تحميل المحافظات. حاول لاحقاً.",
        "select_gov":     "📍 اختر *محافظتك*:",
        "gov_section":    "المحافظات",
        "gov_btn":        "اختر المحافظة",
        "loading_areas":  "📍 جاري تحميل المناطق...",
        "no_areas":       "❌ تعذّر تحميل المناطق. حاول مجدداً.",
        "select_area":    "📍 اختر *منطقتك*:",
        "area_section":   "المناطق",
        "area_btn":       "اختر المنطقة",
        "invalid_area_num": "اختر منطقة من القائمة.",
        "more_options":   "➡️ المزيد من الخيارات",
        "prev_page":      "⬅️ السابق",
        "ask_block":      "🧱 أدخل *رقم القطعة*:",
        "ask_street":     "🛣️ أدخل *اسم أو رقم الشارع*:",
        "reg_summary": (
            "📋 *ملخص التسجيل*\n\n"
            "👤 الاسم: {name}\n"
            "📱 الهاتف: {phone}\n"
            "🧱 القطعة: {block}\n"
            "🛣️ الشارع: {street}\n\n"
            "هل كل شيء صحيح؟ أكّد لإتمام التسجيل."
        ),
        "btn_confirm":    "تأكيد",
        "btn_cancel_reg": "إلغاء",
        "registering":    "⏳ جاري إنشاء حسابك...",
        "reg_fail":       "❌ فشل التسجيل: {err}\n\nحاول مجدداً، أو اكتب *مرحبا* للبدء من جديد.",
        "reg_success":    "✅ أهلاً بك في Servio، *{name}*! تم إنشاء حسابك بنجاح.",

        # Errors
        "generic_error": "⚠️ عذراً، حدث خطأ ما. اكتب *مرحبا* للمحاولة مجدداً.",
        "invalid_gov":   "اختر محافظة من القائمة.",
        "invalid_area":  "اختر منطقة من القائمة.",
        "invalid_prob":  "اختر نوع المشكلة من القائمة.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Return translated string, falling back to English when key is missing."""
    msg = _T.get(lang, _T["en"]).get(key) or _T["en"].get(key, key)
    return msg.format(**kwargs) if kwargs else msg
