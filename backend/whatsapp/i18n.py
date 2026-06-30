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
        "svc_orders_desc":   "View your recent orders",
        "svc_contracts":     "My Contracts",
        "svc_contracts_desc":"View active contracts",
        "svc_invoices":      "My Invoices",
        "svc_invoices_desc": "View your invoices",
        "svc_create":        "Create Service Request",
        "svc_create_desc":   "Schedule a cash call visit",
        "svc_menu":          "Main Menu",
        "svc_menu_desc":     "Return to main menu",
        "svc_list_btn":      "Select Option",

        # Phone lookup
        "ask_phone":    "Please enter your registered phone number:",
        "looking_up":   "🔍 Looking up your account...",
        "not_found":    "❌ No account found for that number.\n\nWould you like to register?",
        "btn_register": "Register Now",
        "btn_retry":    "Try Again",
        "btn_main":     "Main Menu",

        # Account data
        "orders_header":    "📦 *Your Recent Orders:*\n",
        "no_orders":        "📦 No orders found for your account.",
        "contracts_header": "📄 *Your Contracts:*\n",
        "no_contracts":     "📄 No contracts found for your account.",
        "invoices_header":  "🧾 *Your Invoices:*\n",
        "no_invoices":      "🧾 No invoices found for your account.",

        # Service request
        "loading_problems":  "🔍 Loading problem types...",
        "no_problems":       "❌ Could not load problem types. Please try again.",
        "select_problem":    "🔧 *Create Service Request*\n\nPlease select the type of issue:",
        "problem_section":   "Problem Types",
        "more_problems":     "More Types",
        "select_prob_btn":   "Select Problem",
        "ask_description":   "Please describe the issue briefly\n(e.g. *AC not working*, *water leak*):",
        "order_summary":     "🔧 *Service Request Summary*\n\nIssue: {desc}\n\nSubmit for your primary location?",
        "btn_yes_submit":    "Yes, Submit",
        "btn_cancel":        "Cancel",
        "submitting":        "⏳ Submitting your service request...",
        "order_success":     "✅ Request submitted!\n\nOur team will contact you shortly.",
        "order_fail":        "❌ Could not submit: {err}",
        "order_cancelled":   "Request cancelled.",

        # Help
        "help_text": (
            "📞 *Servio Support*\n\n"
            "For assistance please contact our call center.\n\n"
            "Type *hi* or *menu* to return to the main menu."
        ),

        # Registration
        "ask_name":       "Let's get you registered! 📋\n\nPlease enter your *full name*:",
        "ask_phone_reg":  "Great, *{name}*! 👍\n\nNow enter your *phone number*:",
        "loading_govs":   "📍 Fetching governorates...",
        "no_govs":        "❌ Could not load governorates. Please try again later.",
        "select_gov":     "Please select your *governorate*:",
        "gov_section":    "Governorates",
        "gov_btn":        "Choose Governorate",
        "loading_areas":  "📍 Fetching areas...",
        "no_areas":       "❌ Could not load areas. Please try again.",
        "select_area":    "Please select your *area*:",
        "area_section":   "Areas",
        "area_section2":  "More Areas",
        "area_btn":       "Choose Area",
        "ask_block":      "Please enter your *block number*:",
        "ask_street":     "Please enter your *street name or number*:",
        "reg_summary": (
            "📋 *Registration Summary*\n\n"
            "Name:   {name}\nPhone:  {phone}\n"
            "Block:  {block}\nStreet: {street}\n\n"
            "Confirm to complete registration."
        ),
        "btn_confirm":    "Confirm",
        "btn_cancel_reg": "Cancel",
        "registering":    "⏳ Creating your account...",
        "reg_fail":       "❌ Registration failed: {err}\n\nType *hi* to start over.",
        "reg_success":    "✅ Welcome to Servio, *{name}*! Your account has been created.",

        # Errors
        "generic_error": "Sorry, something went wrong. Please type *hi* to try again.",
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
        "svc_orders_desc":   "عرض طلباتك الأخيرة",
        "svc_contracts":     "عقودي",
        "svc_contracts_desc":"عرض العقود النشطة",
        "svc_invoices":      "فواتيري",
        "svc_invoices_desc": "عرض فواتيرك",
        "svc_create":        "طلب خدمة",
        "svc_create_desc":   "جدولة زيارة صيانة",
        "svc_menu":          "القائمة الرئيسية",
        "svc_menu_desc":     "العودة للقائمة",
        "svc_list_btn":      "اختر خياراً",

        # Phone lookup
        "ask_phone":    "الرجاء إدخال رقم هاتفك المسجل:",
        "looking_up":   "🔍 جاري البحث عن حسابك...",
        "not_found":    "❌ لم يُعثر على حساب بهذا الرقم.\n\nهل تريد التسجيل كعميل جديد؟",
        "btn_register": "سجّل الآن",
        "btn_retry":    "حاول مجدداً",
        "btn_main":     "القائمة",

        # Account data
        "orders_header":    "📦 *طلباتك الأخيرة:*\n",
        "no_orders":        "📦 لا توجد طلبات في حسابك.",
        "contracts_header": "📄 *عقودك:*\n",
        "no_contracts":     "📄 لا توجد عقود في حسابك.",
        "invoices_header":  "🧾 *فواتيرك:*\n",
        "no_invoices":      "🧾 لا توجد فواتير في حسابك.",

        # Service request
        "loading_problems": "🔍 جاري تحميل أنواع المشاكل...",
        "no_problems":      "❌ تعذّر تحميل أنواع المشاكل. حاول مجدداً.",
        "select_problem":   "🔧 *طلب خدمة جديد*\n\nاختر نوع المشكلة:",
        "problem_section":  "أنواع المشاكل",
        "more_problems":    "المزيد",
        "select_prob_btn":  "اختر المشكلة",
        "ask_description":  "صف المشكلة بإيجاز\n(مثال: *المكيف لا يعمل*، *تسرب مياه*):",
        "order_summary":    "🔧 *ملخص طلب الخدمة*\n\nالمشكلة: {desc}\n\nإرسال الطلب لموقعك الأساسي؟",
        "btn_yes_submit":   "نعم، أرسل",
        "btn_cancel":       "إلغاء",
        "submitting":       "⏳ جاري إرسال طلبك...",
        "order_success":    "✅ تم إرسال الطلب!\n\nسيتصل بك فريقنا قريباً.",
        "order_fail":       "❌ تعذّر الإرسال: {err}",
        "order_cancelled":  "تم إلغاء الطلب.",

        # Help
        "help_text": (
            "📞 *دعم Servio*\n\n"
            "للمساعدة تواصل مع مركز الاتصال.\n\n"
            "اكتب *مرحبا* للعودة للقائمة."
        ),

        # Registration
        "ask_name":       "لنقم بتسجيلك! 📋\n\nأدخل *اسمك الكامل*:",
        "ask_phone_reg":  "ممتاز، *{name}*! 👍\n\nأدخل *رقم هاتفك*:",
        "loading_govs":   "📍 جاري تحميل المحافظات...",
        "no_govs":        "❌ تعذّر تحميل المحافظات. حاول لاحقاً.",
        "select_gov":     "اختر *محافظتك*:",
        "gov_section":    "المحافظات",
        "gov_btn":        "اختر المحافظة",
        "loading_areas":  "📍 جاري تحميل المناطق...",
        "no_areas":       "❌ تعذّر تحميل المناطق. حاول مجدداً.",
        "select_area":    "اختر *منطقتك*:",
        "area_section":   "المناطق",
        "area_section2":  "مناطق أخرى",
        "area_btn":       "اختر المنطقة",
        "ask_block":      "أدخل *رقم القطعة*:",
        "ask_street":     "أدخل *اسم أو رقم الشارع*:",
        "reg_summary": (
            "📋 *ملخص التسجيل*\n\n"
            "الاسم:    {name}\nالهاتف:  {phone}\n"
            "القطعة: {block}\nالشارع:  {street}\n\n"
            "أكّد لإتمام التسجيل."
        ),
        "btn_confirm":    "تأكيد",
        "btn_cancel_reg": "إلغاء",
        "registering":    "⏳ جاري إنشاء حسابك...",
        "reg_fail":       "❌ فشل التسجيل: {err}\n\nاكتب *مرحبا* للمحاولة مجدداً.",
        "reg_success":    "✅ أهلاً بك في Servio، *{name}*! تم إنشاء حسابك.",

        # Errors
        "generic_error": "عذراً، حدث خطأ. اكتب *مرحبا* للمحاولة مجدداً.",
        "invalid_gov":   "اختر محافظة من القائمة.",
        "invalid_area":  "اختر منطقة من القائمة.",
        "invalid_prob":  "اختر نوع المشكلة من القائمة.",
    },
}


def t(lang: str, key: str, **kwargs) -> str:
    """Return translated string, falling back to English when key is missing."""
    msg = _T.get(lang, _T["en"]).get(key) or _T["en"].get(key, key)
    return msg.format(**kwargs) if kwargs else msg
