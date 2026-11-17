import os
import time
import datetime
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
import psycopg2
from psycopg2 import pool

# ================= CONFIGURATION =================
BOT_TOKEN = "9109714291:AAGpK80XtBacAcm8VRnThBBR4t7CxxK6lKM"
SASTA_API_KEY = "stp_4905928f4de82481bad70ffd7d8da6b59e82e625396bebc3"
BASE_URL = "https://sastasms.pro/stubs/handler_api.php"

DATABASE_URL = "postgresql://neondb_owner:npg_Hy4LqEYdOvk7@ep-weathered-river-bdjtcb91-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require"

MAIN_ADMIN = 8539777823           # @ub2_q
SECOND_ADMIN = 9013970075         # @Worldsim_hub

ALL_ADMINS = [MAIN_ADMIN, SECOND_ADMIN]

UPI_ID_1 = "alone..hacker@ybl"    # Primary UPI
UPI_ID_2 = "noname0011@axl"       # Backup UPI
MERCHANT_NAME = "WorldSIM Store"

SUPPORT_USERNAME = "@Worldsim_hub"
SUPPORT_LINK = "https://t.me/Worldsim_hub"

RECEIPT_CHANNEL_ID = -1004497033717
UPDATE_CHANNEL_ID  = -1003965474093

PROOFS_CHANNEL_LINK   = "https://t.me/+3gxG5EZyJ2UzY2Rl"
OFFICIAL_CHANNEL_LINK = "https://t.me/smmupdatess"

CHANNELS = [
    {
        "id": RECEIPT_CHANNEL_ID,
        "name": "🧾 Official Receipts & Proofs",
        "link": PROOFS_CHANNEL_LINK
    },
    {
        "id": UPDATE_CHANNEL_ID,
        "name": "📢 Bot Updates Channel",
        "link": OFFICIAL_CHANNEL_LINK
    }
]

FORCE_JOIN_IMAGE = "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&auto=format&fit=crop&q=80"
MAIN_MENU_IMAGE  = "https://images.unsplash.com/photo-1557821552-17105176677c?w=800&auto=format&fit=crop&q=80"
BROADCAST_IMAGE  = "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800&auto=format&fit=crop&q=80"

SERVICE_IMAGES = {
    "wa": "https://images.unsplash.com/photo-1614680376593-902f749f7ffc?w=800&auto=format&fit=crop&q=80",
    "tg": "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=80",
    "go": "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=800&auto=format&fit=crop&q=80",
    "ig": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?w=800&auto=format&fit=crop&q=80",
    "fb": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=800&auto=format&fit=crop&q=80"
}

REFER_COMMISSION_PERCENT = 5.0
ITEMS_PER_PAGE = 8

SERVICES = {
    "tg": {"name": "Telegram", "icon": "✈️"},
    "wa": {"name": "WhatsApp", "icon": "💬"},
    "go": {"name": "Google / Gmail", "icon": "🌐"},
    "ig": {"name": "Instagram", "icon": "📸"},
    "fb": {"name": "Facebook", "icon": "📘"}
}

CATALOG = {
    "tg": [
        {"id": "6",   "name": "Indonesia",      "flag": "🇮🇩", "price": 28.56},
        {"id": "34",  "name": "Chile",          "flag": "🇨🇱", "price": 34.21},
        {"id": "26",  "name": "Colombia",       "flag": "🇨🇴", "price": 36.00},
        {"id": "3",   "name": "China",          "flag": "🇨🇳", "price": 46.00},
        {"id": "36",  "name": "Canada",         "flag": "🇨🇦", "price": 55.00},
        {"id": "8",   "name": "Kenya",          "flag": "🇰🇪", "price": 56.90},
        {"id": "81",  "name": "Nepal",          "flag": "🇳🇵", "price": 63.40},
        {"id": "60",  "name": "Bangladesh",     "flag": "🇧🇩", "price": 65.32},
        {"id": "22",  "name": "India",          "flag": "🇮🇳", "price": 76.75},
        {"id": "12",  "name": "USA",            "flag": "🇺🇸", "price": 60.00},
        {"id": "16",  "name": "United Kingdom", "flag": "🇬🇧", "price": 130.00}
    ],
    "wa": [
        {"id": "6",   "name": "Indonesia",      "flag": "🇮🇩", "price": 52.18},
        {"id": "34",  "name": "Chile",          "flag": "🇨🇱", "price": 58.90},
        {"id": "12",  "name": "USA (2)",        "flag": "🇺🇸", "price": 69.40},
        {"id": "26",  "name": "Colombia",       "flag": "🇨🇴", "price": 58.90},
        {"id": "107", "name": "South Africa",   "flag": "🇿🇦", "price": 72.00},
        {"id": "70",  "name": "Barbados",       "flag": "🇧🇧", "price": 77.00},
        {"id": "10",  "name": "Vietnam",        "flag": "🇻🇳", "price": 82.00},
        {"id": "64",  "name": "Sri Lanka",      "flag": "🇱🇰", "price": 86.00},
        {"id": "36",  "name": "Canada",         "flag": "🇨🇦", "price": 94.00},
        {"id": "148", "name": "Greenland",      "flag": "🇬🇱", "price": 107.00},
        {"id": "153", "name": "Iceland",        "flag": "🇮🇸", "price": 140.00},
        {"id": "16",  "name": "United Kingdom", "flag": "🇬🇧", "price": 106.00},
        {"id": "22",  "name": "India",          "flag": "🇮🇳", "price": 150.00},
        {"id": "66",  "name": "Pakistan",       "flag": "🇵🇰", "price": 70.00}
    ],
    "go": [
        {"id": "6",   "name": "Indonesia",      "flag": "🇮🇩", "price": 22.00},
        {"id": "26",  "name": "Colombia",       "flag": "🇨🇴", "price": 25.00},
        {"id": "12",  "name": "USA (Server 2)", "flag": "🇺🇸", "price": 28.00}
    ],
    "ig": [
        {"id": "6",   "name": "Indonesia",      "flag": "🇮🇩", "price": 20.00},
        {"id": "26",  "name": "Colombia",       "flag": "🇨🇴", "price": 24.00},
        {"id": "12",  "name": "USA (Server 2)", "flag": "🇺🇸", "price": 28.00}
    ],
    "fb": [
        {"id": "6",   "name": "Indonesia",      "flag": "🇮🇩", "price": 18.00},
        {"id": "26",  "name": "Colombia",       "flag": "🇨🇴", "price": 22.00},
        {"id": "12",  "name": "USA (Server 2)", "flag": "🇺🇸", "price": 25.00}
    ]
}

active_orders = {}
user_search_state = {}
user_recent_orders = {}
BOT_USERNAME_CACHE = None
# =================================================

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"WorldSIM OTP Store Running 24/7!")

    def log_message(self, format, *args):
        return

def run_http_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_http_server, daemon=True).start()

telebot.apihelper.READ_TIMEOUT = 60
telebot.apihelper.CONNECT_TIMEOUT = 30

bot = telebot.TeleBot(BOT_TOKEN, threaded=True, num_threads=4)

def get_bot_username():
    global BOT_USERNAME_CACHE
    if not BOT_USERNAME_CACHE:
        try:
            BOT_USERNAME_CACHE = bot.get_me().username
        except Exception:
            BOT_USERNAME_CACHE = "WorldsimOtp_bot"
    return BOT_USERNAME_CACHE

# ================= DATABASE =================
db_pool = None

def get_pool():
    global db_pool
    if db_pool is None:
        db_pool = pool.ThreadedConnectionPool(1, 10, DATABASE_URL)
    return db_pool

def get_db_conn():
    return get_pool().getconn()

def release_db_conn(conn):
    if conn:
        get_pool().putconn(conn)

def init_db():
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                balance REAL DEFAULT 0.0,
                referred_by BIGINT DEFAULT 0
            );
            """)
        conn.commit()
    except Exception as e:
        print(f"Database Init Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

init_db()

user_dep_cache = {}

def get_user(uid):
    uid = int(uid)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT balance, referred_by FROM users WHERE user_id = %s;", (uid,))
            r = cur.fetchone()
            if r:
                return float(r[0]), int(r[1])
            cur.execute("INSERT INTO users (user_id, balance, referred_by) VALUES (%s, 0.0, 0) ON CONFLICT DO NOTHING;", (uid,))
        conn.commit()
        return 0.0, 0
    except Exception as e:
        print(f"get_user Error: {e}")
        return 0.0, 0
    finally:
        if conn:
            release_db_conn(conn)

def get_bal(uid):
    bal, _ = get_user(uid)
    return bal

def update_bal(uid, amt):
    uid = int(uid)
    amt = float(amt)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO users (user_id, balance, referred_by) 
            VALUES (%s, GREATEST(0.0, %s), 0)
            ON CONFLICT (user_id) 
            DO UPDATE SET balance = GREATEST(0.0, users.balance + %s)
            RETURNING balance;
            """, (uid, amt, amt))
            new_bal = cur.fetchone()[0]
        conn.commit()
        return round(float(new_bal), 2)
    except Exception as e:
        print(f"update_bal Error: {e}")
        return 0.0
    finally:
        if conn:
            release_db_conn(conn)

def set_referrer(uid, ref_id):
    uid = int(uid)
    ref_id = int(ref_id)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT referred_by FROM users WHERE user_id = %s;", (uid,))
            r = cur.fetchone()
            if not r:
                cur.execute("INSERT INTO users (user_id, balance, referred_by) VALUES (%s, 0.0, %s);", (uid, ref_id))
            elif r[0] == 0 and uid != ref_id:
                cur.execute("UPDATE users SET referred_by = %s WHERE user_id = %s;", (ref_id, uid))
        conn.commit()
    except Exception as e:
        print(f"set_referrer Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

# ================= FORCE JOIN =================
def get_user_unjoined_channels(uid):
    if uid in ALL_ADMINS:
        return []
    unjoined = []
    for ch in CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], uid)
            if member.status not in ['creator', 'administrator', 'member', 'restricted']:
                unjoined.append(ch)
        except Exception:
            pass
    return unjoined

def is_user_member(uid):
    return len(get_user_unjoined_channels(uid)) == 0

def get_force_join_menu():
    mk = InlineKeyboardMarkup(row_width=1)
    for ch in CHANNELS:
        mk.add(InlineKeyboardButton(f"{ch['name']}", url=ch["link"]))
    mk.add(InlineKeyboardButton("✅ Verify & Continue", callback_data="check_join"))
    return mk

def send_force_join_prompt(chat_id):
    caption = (
        "🔒 <b>Mandatory Verification Required</b>\n\n"
        "Store ke features aur OTP numbers purchase karne ke liye dono channels join karein:\n\n"
        "1️⃣ <b>Official Receipts & Proofs</b>\n"
        "2️⃣ <b>Bot Updates Channel</b>\n\n"
        "👇 <b>Dono join karke 'Verify & Continue' dabayein:</b>"
    )
    try:
        bot.send_photo(chat_id, photo=FORCE_JOIN_IMAGE, caption=caption, reply_markup=get_force_join_menu(), parse_mode="HTML")
    except Exception:
        bot.send_message(chat_id, caption, reply_markup=get_force_join_menu(), parse_mode="HTML")

def generate_dynamic_qr_url(upi_id, amount):
    note = f"Store_{int(time.time())}"
    upi_string = f"upi://pay?pa={upi_id}&pn={urllib.parse.quote(MERCHANT_NAME)}&am={amount:.2f}&cu=INR&tn={note}"
    return f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_string)}"

def format_user_tag(buyer_id, buyer_username):
    if buyer_username and buyer_username.strip():
        u = buyer_username.replace("@", "")
        return f"@{u}"
    str_uid = str(buyer_id)
    return str_uid[:2] + "••••" + str_uid[-2:] if len(str_uid) > 4 else "••••" + str_uid[-2:]

def send_sale_receipt(service_name, country_name, country_flag, phone_num, activation_id, price_inr, buyer_id, buyer_username):
    user_tag = format_user_tag(buyer_id, buyer_username)
    str_phone = str(phone_num)
    masked_phone = str_phone[:4] + "••••" + str_phone[-2:] if len(str_phone) > 6 else str_phone[:2] + "••••"

    now_str = datetime.datetime.now().strftime("%d %b %Y  %H:%M")
    price_usd = round(price_inr / 88.0, 2)

    receipt = (
        "+--------------------------------------+\n"
        "|     WORLDSIM  •  SALE RECEIPT        |\n"
        "+--------------------------------------+\n"
        "|                                      |\n"
        f"|  Status     : PURCHASED OK           |\n"
        f"|  Buyer      : {user_tag:<23}|\n"
        f"|  Service    : {service_name.upper():<23}|\n"
        f"|  Country    : {country_name} {country_flag:<16}|\n"
        f"|  Item ID    : {activation_id:<23}|\n"
        f"|  Number     : +{masked_phone:<22}|\n"
        f"|  Price USD  : ${price_usd:<22.2f}|\n"
        f"|  Price INR  : Rs.{price_inr:<20.2f}|\n"
        f"|  Time       : {now_str:<23}|\n"
        "|                                      |\n"
        "+--------------------------------------+"
    )
    bot_uname = get_bot_username()
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton("🛒 Buy Number", url=f"https://t.me/{bot_uname}?start=buy"))

    try:
        bot.send_message(RECEIPT_CHANNEL_ID, f"```\n{receipt}\n```", reply_markup=mk, parse_mode="Markdown")
    except Exception as e:
        print(f"Receipt channel post error: {e}")

def send_feedback_receipt_to_channel(buyer_id, stars, service_name, buyer_username):
    user_tag = format_user_tag(buyer_id, buyer_username)
    star_str = "⭐" * stars
    now_str = datetime.datetime.now().strftime("%d %b %Y  %H:%M")

    feedback_msg = (
        "+--------------------------------------+\n"
        "|      WORLDSIM  •  USER FEEDBACK      |\n"
        "+--------------------------------------+\n"
        "|                                      |\n"
        f"|  Customer   : {user_tag:<23}|\n"
        f"|  Service    : {service_name.upper():<23}|\n"
        f"|  Rating     : {star_str:<23}|\n"
        f"|  Date/Time  : {now_str:<23}|\n"
        "|                                      |\n"
        "+--------------------------------------+\n"
        "|      TRUSTED & VERIFIED PURCHASE     |\n"
        "+--------------------------------------+"
    )
    bot_uname = get_bot_username()
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton("🛒 Buy Number", url=f"https://t.me/{bot_uname}?start=buy"))

    try:
        bot.send_message(RECEIPT_CHANNEL_ID, f"```\n{feedback_msg}\n```", reply_markup=mk, parse_mode="Markdown")
    except Exception as e:
        print(f"Feedback error: {e}")

def get_feedback_menu(service_name):
    mk = InlineKeyboardMarkup(row_width=5)
    mk.row(
        InlineKeyboardButton("1 ⭐", callback_data=f"rate_1_{service_name}"),
        InlineKeyboardButton("2 ⭐", callback_data=f"rate_2_{service_name}"),
        InlineKeyboardButton("3 ⭐", callback_data=f"rate_3_{service_name}"),
        InlineKeyboardButton("4 ⭐", callback_data=f"rate_4_{service_name}"),
        InlineKeyboardButton("5 ⭐", callback_data=f"rate_5_{service_name}")
    )
    return mk

def get_service_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛒 BROWSE SERVICES", callback_data="open_browse_services")
    )
    markup.add(
        InlineKeyboardButton("💳 ADD BALANCE", callback_data="menu_dep"),
        InlineKeyboardButton("📦 MY ORDERS", callback_data="menu_orders")
    )
    markup.add(
        InlineKeyboardButton("👤 MY PROFILE", callback_data="menu_profile"),
        InlineKeyboardButton("🛠️ SUPPORT ↗", url=SUPPORT_LINK)
    )
    markup.add(
        InlineKeyboardButton("📢 OFFICIAL CHANNEL ↗", url=OFFICIAL_CHANNEL_LINK),
        InlineKeyboardButton("🧾 PAYMENT PROOFS ↗", url=PROOFS_CHANNEL_LINK)
    )
    return markup

def get_service_picker_menu():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("✈️ Telegram OTP", callback_data="page_tg_0"),
        InlineKeyboardButton("💬 WhatsApp OTP", callback_data="page_wa_0")
    )
    markup.add(
        InlineKeyboardButton("🌐 Google/Gmail OTP", callback_data="page_go_0"),
        InlineKeyboardButton("📸 Instagram OTP", callback_data="page_ig_0")
    )
    markup.add(
        InlineKeyboardButton("📘 Facebook OTP", callback_data="page_fb_0")
    )
    markup.add(InlineKeyboardButton("🏠 Back to Home", callback_data="back_main"))
    return markup

def get_countries_paged_menu(service, page=0):
    markup = InlineKeyboardMarkup(row_width=2)
    country_list = CATALOG.get(service, [])
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_page_items = country_list[start_idx:end_idx]
    total_pages = (len(country_list) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    btns = []
    for c in current_page_items:
        cid = c["id"]
        price = c["price"]
        btn_text = f"{c['flag']} {c['name']} | Rs {price}"
        btns.append(InlineKeyboardButton(text=btn_text, callback_data=f"buy_{service}_{cid}_{price}"))

    for i in range(0, len(btns), 2):
        markup.row(*btns[i:i+2])

    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"page_{service}_{page-1}"))
    if total_pages > 1:
        nav_row.append(InlineKeyboardButton(f"📄 {page+1}/{total_pages}", callback_data="ignore"))
    if end_idx < len(country_list):
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"page_{service}_{page+1}"))

    if nav_row:
        markup.row(*nav_row)

    markup.add(InlineKeyboardButton("🔍 Search Country", callback_data=f"search_country_{service}"))
    markup.add(InlineKeyboardButton("🔙 Services List", callback_data="open_browse_services"))
    return markup

def get_deposit_menu():
    mk = InlineKeyboardMarkup(row_width=2)
    mk.add(
        InlineKeyboardButton("Rs 20", callback_data="setdep_20"),
        InlineKeyboardButton("Rs 50", callback_data="setdep_50"),
        InlineKeyboardButton("Rs 100", callback_data="setdep_100"),
        InlineKeyboardButton("Rs 200", callback_data="setdep_200")
    )
    mk.add(InlineKeyboardButton("🏠 Back to Home", callback_data="back_main"))
    return mk

def get_qr_toggle_menu(active_upi_num, amt):
    mk = InlineKeyboardMarkup(row_width=2)
    b1 = "✅ Primary UPI" if active_upi_num == 1 else "Switch to Primary UPI"
    b2 = "✅ Backup UPI" if active_upi_num == 2 else "Switch to Backup UPI"
    mk.add(
        InlineKeyboardButton(b1, callback_data=f"toggle_upi_1_{amt}"),
        InlineKeyboardButton(b2, callback_data=f"toggle_upi_2_{amt}")
    )
    return mk

def send_payment_qr(chat_id, uid, amount, upi_choice=1):
    chosen_upi = UPI_ID_1 if upi_choice == 1 else UPI_ID_2
    user_dep_cache[uid] = {"amt": amount, "upi": upi_choice}
    qr_url = generate_dynamic_qr_url(chosen_upi, amount)

    caption = (
        f"💳 <b>Deposit Amount: Rs {amount:.2f}</b>\n\n"
        f"Is QR ko scan karke payment karein!\n\n"
        f"UPI ID: <code>{chosen_upi}</code>\n\n"
        f"Support: {SUPPORT_USERNAME}\n\n"
        f"⚠️ <b>Important:</b> Payment hote hi uska <b>Screenshot</b> send karein approval ke liye."
    )
    bot.send_photo(chat_id, qr_url, caption=caption, reply_markup=get_qr_toggle_menu(upi_choice, amount), parse_mode="HTML")

# ================= 20-MINUTE POLLING LOOP =================
def poll_otp_20_minutes(cid, uid, activation_id, price, service_name, status_msg_id):
    active_orders[activation_id] = {"status": "waiting"}
    status_url = f"{BASE_URL}?api_key={SASTA_API_KEY}&action=getStatus&id={activation_id}"
    cancel_url = f"{BASE_URL}?api_key={SASTA_API_KEY}&action=setStatus&status=8&id={activation_id}"
    
    max_checks = 300
    
    for check in range(max_checks):
        time.sleep(4)
        if active_orders.get(activation_id, {}).get("status") == "cancelled_by_user":
            del active_orders[activation_id]
            return

        try:
            r = requests.get(status_url, timeout=5)
            text_res = r.text.strip()

            if "STATUS_OK" in text_res:
                parts = text_res.split(":")
                otp = parts[1] if len(parts) > 1 else text_res
               
