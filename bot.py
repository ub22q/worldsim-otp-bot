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
                if otp and otp.lower() != "none":
                    bot.send_message(cid, f"✅ <b>Aapka OTP Code:</b> <code>{otp}</code>", parse_mode="HTML")
                    time.sleep(1)
                    bot.send_message(
                        cid,
                        f"🌟 <b>Order Complete!</b>\n\nAapko hamari <b>{service_name}</b> service kaisi lagi? Rate karein:",
                        reply_markup=get_feedback_menu(service_name),
                        parse_mode="HTML"
                    )
                    if activation_id in active_orders:
                        del active_orders[activation_id]
                    return

            elif "STATUS_CANCEL" in text_res:
                new_bal = update_bal(uid, price)
                bot.send_message(cid, f"❌ Order server dwara cancel kar diya gaya.\n<b>Rs {price:.2f} refund kar diye gaye hain!</b>\nWallet Balance: <b>Rs {new_bal:.2f}</b>", parse_mode="HTML")
                if activation_id in active_orders:
                    del active_orders[activation_id]
                return
            else:
                try:
                    res = r.json()
                    status = res.get("status", "")
                    if status == "STATUS_OK" or "code" in res:
                        otp = res.get("code") or res.get("sms")
                        if otp and str(otp).lower() != "none":
                            bot.send_message(cid, f"✅ <b>Aapka OTP Code:</b> <code>{otp}</code>", parse_mode="HTML")
                            time.sleep(1)
                            bot.send_message(
                                cid,
                                f"🌟 <b>Order Complete!</b>\n\nAapko hamari <b>{service_name}</b> service kaisi lagi? Rate karein:",
                                reply_markup=get_feedback_menu(service_name),
                                parse_mode="HTML"
                            )
                            if activation_id in active_orders:
                                del active_orders[activation_id]
                            return
                except Exception:
                    pass

        except Exception as e:
            print(f"Polling error: {e}")

    try:
        requests.get(cancel_url, timeout=5)
    except Exception:
        pass

    new_bal = update_bal(uid, price)
    if activation_id in active_orders:
        del active_orders[activation_id]

    timeout_msg = (
        f"⏳ <b>20 Minute Timeout!</b>\n\n"
        f"20 minute me OTP receive nahi hua. Order cancel kar diya gaya hai.\n\n"
        f"💰 <b>Refund:</b> Rs {price:.2f} wallet me wapas add ho gaye hain.\n"
        f"Current Balance: <b>Rs {new_bal:.2f}</b>"
    )
    bot.send_message(cid, timeout_msg, parse_mode="HTML")

# ================= ADMIN ACTIONS & BROADCAST =================
@bot.message_handler(commands=["addbalance", "addbal", "givebal"])
def admin_add_balance(m):
    uid = m.from_user.id
    if uid not in ALL_ADMINS:
        return

    parts = m.text.split()
    if len(parts) < 3:
        bot.reply_to(m, "Format: <code>/addbalance <user_id> <amount></code>", parse_mode="HTML")
        return

    try:
        target_uid = int(parts[1])
        amount = float(parts[2])
    except ValueError:
        bot.reply_to(m, "User ID aur Amount sahi numbers hone chahiye!")
        return

    if amount <= 0:
        bot.reply_to(m, "Amount 0 se bada hona chahiye!")
        return

    new_bal = update_bal(target_uid, amount)
    bot.reply_to(m, f"✅ Added Rs {amount:.2f} to <code>{target_uid}</code>\nNaya Balance: Rs {new_bal:.2f}", parse_mode="HTML")

    try:
        bot.send_message(target_uid, f"🎉 <b>Wallet me Rs {amount:.2f} add ho gaye hain!</b>\nBalance: <b>Rs {new_bal:.2f}</b>", parse_mode="HTML")
    except Exception:
        pass

@bot.message_handler(commands=["checkbalance", "checkbal", "userbal"])
def admin_check_user_balance(m):
    uid = m.from_user.id
    if uid not in ALL_ADMINS:
        return

    parts = m.text.split()
    if len(parts) < 2:
        bot.reply_to(m, "Format: <code>/checkbalance <user_id></code>\nExample: <code>/checkbalance 9013970075</code>", parse_mode="HTML")
        return

    try:
        target_uid = int(parts[1])
    except ValueError:
        bot.reply_to(m, "User ID ek valid number honi chahiye!")
        return

    user_bal, ref_by = get_user(target_uid)
    info_text = (
        f"👤 <b>User Wallet Details:</b>\n\n"
        f"• <b>User ID:</b> <code>{target_uid}</code>\n"
        f"• <b>Current Balance:</b> <b>Rs {user_bal:.2f}</b>\n"
        f"• <b>Referred By:</b> <code>{ref_by if ref_by != 0 else 'None'}</code>"
    )
    bot.reply_to(m, info_text, parse_mode="HTML")

@bot.message_handler(commands=["cutbalance", "cutbal", "removebal", "deductbal"])
def admin_cut_balance(m):
    uid = m.from_user.id
    if uid not in ALL_ADMINS:
        return

    parts = m.text.split()
    if len(parts) < 3:
        bot.reply_to(m, "Format: <code>/cutbalance <user_id> <amount></code>\nExample: <code>/cutbalance 9013970075 50</code>", parse_mode="HTML")
        return

    try:
        target_uid = int(parts[1])
        amount = float(parts[2])
    except ValueError:
        bot.reply_to(m, "User ID aur Amount sahi numbers hone chahiye!")
        return

    if amount <= 0:
        bot.reply_to(m, "Amount 0 se bada hona chahiye!")
        return

    current_bal = get_bal(target_uid)
    if current_bal <= 0:
        bot.reply_to(m, f"⚠️ User <code>{target_uid}</code> ka balance pehle se hi <b>Rs 0.00</b> hai!", parse_mode="HTML")
        return

    new_bal = update_bal(target_uid, -amount)
    bot.reply_to(
        m,
        f"✂️ <b>Balance Deducted!</b>\n\n"
        f"• User ID: <code>{target_uid}</code>\n"
        f"• Deducted Amount: <b>Rs {amount:.2f}</b>\n"
        f"• Remaining Balance: <b>Rs {new_bal:.2f}</b>",
        parse_mode="HTML"
    )

    try:
        bot.send_message(
            target_uid,
            f"⚠️ <b>Wallet Update:</b>\n\nAdmin dwara aapke wallet se <b>Rs {amount:.2f}</b> deduct kar liye gaye hain.\nNaya Balance: <b>Rs {new_bal:.2f}</b>",
            parse_mode="HTML"
        )
    except Exception:
        pass

@bot.message_handler(commands=["update", "botupdate"])
def send_update_to_all(m):
    uid = m.from_user.id
    if uid not in ALL_ADMINS:
        return

    custom_text = m.text.replace("/update", "").replace("/botupdate", "").strip()

    if not custom_text:
        update_caption = (
            "🚀 <b>WorldSIM Store Live!</b>\n\n"
            "Naye fast OTP servers aur updated features live ho chuke hain:\n\n"
            "✨ <b>Features:</b>\n"
            "• Direct WhatsApp & Telegram OTPs\n"
            "• 20 Min auto cancel & instant refund\n"
            f"• 24/7 Support: {SUPPORT_USERNAME}\n\n"
            "👉 Neeche diye gaye button se start karein!"
        )
    else:
        update_caption = f"🚀 <b>Store Notice:</b>\n\n{custom_text}\n\n👉 Neeche diye gaye button se start karein:"

    bot_username = get_bot_username()
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton("🚀 Open Store", url=f"https://t.me/{bot_username}?start=start"))

    conn = None
    all_users = []
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users;")
            all_users = cur.fetchall()
    finally:
        if conn:
            release_db_conn(conn)

    sent = 0
    failed = 0
    bot.reply_to(m, f"📢 Sabhi {len(all_users)} users ko update notice bhejna shuru kar rahe hain...")

    for user in all_users:
        u_id = user[0]
        try:
            bot.send_photo(u_id, photo=BROADCAST_IMAGE, caption=update_caption, reply_markup=mk, parse_mode="HTML")
            sent += 1
            time.sleep(0.05)
        except Exception:
            failed += 1

    bot.send_message(m.chat.id, f"✅ <b>Update Sent!</b>\n\nDelivered: <b>{sent}</b> | Failed: <b>{failed}</b>", parse_mode="HTML")

@bot.message_handler(commands=["broadcast", "sendall"])
def broadcast_message(m):
    uid = m.from_user.id
    if uid not in ALL_ADMINS:
        return

    msg_text = m.text.replace("/broadcast", "").replace("/sendall", "").strip()
    if not msg_text:
        bot.reply_to(m, "Format: <code>/broadcast Message</code>", parse_mode="HTML")
        return

    conn = None
    all_users = []
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM users;")
            all_users = cur.fetchall()
    finally:
        if conn:
            release_db_conn(conn)

    sent = 0
    failed = 0
    for user in all_users:
        u_id = user[0]
        try:
            bot.send_message(u_id, f"📢 <b>Store Announcement:</b>\n\n{msg_text}", parse_mode="HTML")
            sent += 1
            time.sleep(0.05)
        except Exception:
            failed += 1

    bot.send_message(m.chat.id, f"✅ Broadcast Complete!\nDelivered: <b>{sent}</b> | Failed: <b>{failed}</b>", parse_mode="HTML")

# ================= USER ENTRY =================
@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id
    name = m.from_user.first_name or "User"
    parts = m.text.split()

    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            ref_id = int(parts[1].replace("ref_", ""))
            set_referrer(uid, ref_id)
        except Exception:
            pass

    if not is_user_member(uid):
        send_force_join_prompt(m.chat.id)
        return

    if len(parts) > 1 and parts[1] == "buy":
        text = "🛒 <b>Available OTP Services</b>\n\nApni pasandida service select karein:"
        try:
            bot.send_photo(m.chat.id, photo=MAIN_MENU_IMAGE, caption=text, reply_markup=get_service_picker_menu(), parse_mode="HTML")
        except Exception:
            bot.reply_to(m, text, reply_markup=get_service_picker_menu(), parse_mode="HTML")
        return

    bal = get_bal(uid)
    text = (
        f"🌐 <b>Welcome to WorldSIM Hub</b> 🌐\n\n"
        f"👤 Account: <b>{name}</b>\n"
        f"🆔 User ID: <code>{uid}</code>\n"
        f"💰 Balance: <b>Rs {bal:.2f}</b>\n\n"
        f"Select an option from the menu below:"
    )
    try:
        bot.send_photo(m.chat.id, photo=MAIN_MENU_IMAGE, caption=text, reply_markup=get_service_menu(), parse_mode="HTML")
    except Exception:
        bot.reply_to(m, text, reply_markup=get_service_menu(), parse_mode="HTML")

@bot.message_handler(commands=["support", "help"])
def support_cmd(m):
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton("💬 Open Support Chat", url=SUPPORT_LINK))
    bot.reply_to(m, f"24/7 Helpline: {SUPPORT_USERNAME}", reply_markup=mk)

@bot.message_handler(commands=["balance"])
def balance(m):
    if not is_user_member(m.from_user.id):
        send_force_join_prompt(m.chat.id)
        return
    bot.reply_to(m, f"Wallet Balance: Rs {get_bal(m.from_user.id):.2f}")

@bot.message_handler(commands=["deposit"])
def dep(m):
    if not is_user_member(m.from_user.id):
        send_force_join_prompt(m.chat.id)
        return
    bot.reply_to(m, "Deposit amount select karein (Minimum Rs 20):", reply_markup=get_deposit_menu(), parse_mode="HTML")

@bot.message_handler(func=lambda m: not m.text.startswith("/"))
def text_flow(m):
    uid = m.from_user.id
    if not is_user_member(uid):
        send_force_join_prompt(m.chat.id)
        return

    raw = m.text.strip()

    if uid in user_search_state:
        service = user_search_state[uid]
        del user_search_state[uid]
        query = raw.lower()
        country_list = CATALOG.get(service, [])
        matches = [c for c in country_list if query in c["name"].lower()]

        if not matches:
            bot.reply_to(m, f"❌ '<b>{raw}</b>' naam ka koi country nahi mila!\n\nMain menu se list dekhein.", reply_markup=get_service_menu(), parse_mode="HTML")
            return

        mk = InlineKeyboardMarkup(row_width=2)
        btns = []
        for c in matches:
            cid = c["id"]
            price = c["price"]
            btn_text = f"{c['flag']} {c['name']} | Rs {price}"
            btns.append(InlineKeyboardButton(text=btn_text, callback_data=f"buy_{service}_{cid}_{price}"))

        for i in range(0, len(btns), 2):
            mk.row(*btns[i:i+2])
        mk.add(InlineKeyboardButton("🔙 Back to Services", callback_data="open_browse_services"))

        bot.reply_to(m, f"🔍 <b>Search Results for '{raw}':</b>", reply_markup=mk, parse_mode="HTML")
        return

    if raw.isdigit() and len(raw) <= 5:
        amt = float(raw)
        if amt < 20:
            bot.reply_to(m, "⚠️ <b>Minimum deposit Rs 20 hai!</b>\nKripya Rs 20 ya usse jyada type karein.", parse_mode="HTML")
            return
        send_payment_qr(m.chat.id, uid, amt, upi_choice=1)
        return

    bot.reply_to(m, "⚠️ <b>Kripya Payment ka Screenshot send karein!</b>\n\nText UTR accept nahi hota, direct photo bhejein.", parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def photo_flow(m):
    uid = m.from_user.id
    if not is_user_member(uid):
        send_force_join_prompt(m.chat.id)
        return

    amt_data = user_dep_cache.get(uid, {"amt": 20.0, "upi": 1})
    amt = amt_data["amt"]
    cap = m.caption if m.caption else "No Caption"
    name = m.from_user.first_name or "User"
    user_tag = format_user_tag(uid, m.from_user.username)

    mk = InlineKeyboardMarkup()
    mk.row(
        InlineKeyboardButton(f"Approve Rs {int(amt)}", callback_data=f"app_{uid}_{amt}_photo"),
        InlineKeyboardButton("Reject", callback_data=f"rej_{uid}")
    )
    admin_cap = (
        f"<b>Naya Screenshot Deposit!</b>\n"
        f"User: <b>{name}</b> ({user_tag} | <code>{uid}</code>)\n"
        f"Amount: <b>Rs {amt:.2f}</b>\n"
        f"Caption: <code>{cap}</code>"
    )

    for admin in ALL_ADMINS:
        try:
            bot.send_photo(admin, m.photo[-1].file_id, caption=admin_cap, reply_markup=mk, parse_mode="HTML")
        except Exception:
            pass

    bot.reply_to(m, f"✅ Screenshot receive ho gaya! Admin approval ke baad balance add ho jayega.\nSupport: {SUPPORT_USERNAME}", parse_mode="HTML")

# ================= CALLBACK ROUTING =================
@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid = call.from_user.id
    uname = call.from_user.username

    if call.data == "check_join":
        unjoined = get_user_unjoined_channels(uid)
        if len(unjoined) == 0:
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            bal = get_bal(uid)
            name = call.from_user.first_name or "User"
            text = (
                f"✅ <b>Verification Successful!</b>\n\n"
                f"🌐 <b>Welcome to WorldSIM Hub</b> 🌐\n\n"
                f"👤 Account: <b>{name}</b>\n"
                f"🆔 User ID: <code>{uid}</code>\n"
                f"💰 Balance: <b>Rs {bal:.2f}</b>\n\n"
                f"Select an option from the menu below:"
            )
            bot.send_photo(call.message.chat.id, photo=MAIN_MENU_IMAGE, caption=text, reply_markup=get_service_menu(), parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, f"⚠️ Abhi {len(unjoined)} channel(s) baaki hain! Dono join karein.", show_alert=True)
        return

    if call.data == "menu_profile":
        bal = get_bal(uid)
        bu = get_bot_username()
        ref_link = f"https://t.me/{bu}?start=ref_{uid}"

        conn = None
        refs = 0
        try:
            conn = get_db_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM users WHERE referred_by = %s;", (uid,))
                refs = cur.fetchone()[0]
        finally:
            if conn:
                release_db_conn(conn)

        prof_text = (
            f"👤 <b>User Profile</b>\n\n"
            f"• <b>User ID:</b> <code>{uid}</code>\n"
            f"• <b>Username:</b> @{uname if uname else 'Not Set'}\n"
            f"• <b>Wallet Balance:</b> Rs {bal:.2f}\n"
            f"• <b>Referrals:</b> {refs} Users (5% Commission)\n\n"
            f"🔗 <b>Your Referral Link:</b>\n<code>{ref_link}</code>"
        )
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("💳 Add Balance", callback_data="menu_dep"))
        mk.add(InlineKeyboardButton("🏠 Back to Home", callback_data="back_main"))
        bot.send_message(call.message.chat.id, prof_text, reply_markup=mk, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if call.data == "menu_orders":
        last_ord = user_recent_orders.get(uid)
        if not last_ord:
            ord_text = "📦 <b>Aapka koi active order nahi hai.</b>\n\nNaye OTP number lene ke liye 'BROWSE SERVICES' par tap karein."
        else:
            ord_text = (
                f"📦 <b>Recent Order Details:</b>\n\n"
                f"• <b>Service:</b> {last_ord.get('service')}\n"
                f"• <b>Country:</b> {last_ord.get('country')}\n"
                f"• <b>Number:</b> <code>+{last_ord.get('phone')}</code>\n"
                f"• <b>Status:</b> {last_ord.get('status')}"
            )
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🛒 Browse Services", callback_data="open_browse_services"))
        mk.add(InlineKeyboardButton("🏠 Back to Home", callback_data="back_main"))
        bot.send_message(call.message.chat.id, ord_text, reply_markup=mk, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if call.data == "open_browse_services":
        text = "🛒 <b>Available OTP Services</b>\n\nApni pasandida service select karein:"
        if call.message.photo:
            try:
                bot.edit_message_media(
                    media=InputMediaPhoto(MAIN_MENU_IMAGE, caption=text, parse_mode="HTML"),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=get_service_picker_menu()
                )
            except Exception:
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_service_picker_menu(), parse_mode="HTML")
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=get_service_picker_menu(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("search_country_"):
        service = call.data.replace("search_country_", "")
        user_search_state[uid] = service
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"🔍 <b>Country Search</b>\n\nCountry ka naam type karein (Jaise: <code>India</code>, <code>Chile</code>, <code>Canada</code>, <code>UK</code>):",
            parse_mode="HTML"
        )
        return

    if call.data.startswith("rate_"):
        parts = call.data.split("_")
        stars = int(parts[1])
        s_name = parts[2] if len(parts) > 2 else "OTP Service"

        bot.answer_callback_query(call.id, f"Aapne {stars} Star diya! Dhanyawad.")
        thank_you_text = f"💖 <b>Feedback ke liye shukriya!</b>\n\nAapne {'⭐' * stars} rating di hai."
        try:
            bot.edit_message_text(text=thank_you_text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        except Exception:
            bot.send_message(call.message.chat.id, thank_you_text, parse_mode="HTML")

        threading.Thread(target=send_feedback_receipt_to_channel, args=(uid, stars, s_name, uname)).start()
        return

    if call.data.startswith("cancel_order_"):
        parts = call.data.split("_")
        act_id = parts[2]
        refund_price = float(parts[3])

        if act_id in active_orders:
            active_orders[act_id]["status"] = "cancelled_by_user"

        cancel_url = f"{BASE_URL}?api_key={SASTA_API_KEY}&action=setStatus&status=8&id={act_id}"
        try:
            requests.get(cancel_url, timeout=5)
        except Exception:
            pass

        new_bal = update_bal(uid, refund_price)
        if uid in user_recent_orders:
            user_recent_orders[uid]["status"] = "Cancelled & Refunded"

        bot.answer_callback_query(call.id, "Order cancelled! Amount refunded.")
        bot.edit_message_text(
            f"❌ <b>Order Cancelled!</b>\n\nRs {refund_price:.2f} aapke wallet me refund kar diye gaye hain.\nCurrent Balance: <b>Rs {new_bal:.2f}</b>",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            parse_mode="HTML"
        )
        return

    if not is_user_member(uid) and uid not in ALL_ADMINS:
        bot.answer_callback_query(call.id, "⚠️ Pehle dono channels join karein!", show_alert=True)
        return

    bal = get_bal(uid)

    if call.data == "ignore":
        bot.answer_callback_query(call.id)
    elif call.data == "back_main":
        text = (
            f"🌐 <b>Welcome to WorldSIM Hub</b> 🌐\n\n"
            f"👤 Account: <b>{call.from_user.first_name}</b>\n"
            f"🆔 User ID: <code>{uid}</code>\n"
            f"💰 Balance: <b>Rs {bal:.2f}</b>\n\n"
            f"Select an option from the menu below:"
        )
        if call.message.photo:
            try:
                bot.edit_message_media(
                    media=InputMediaPhoto(MAIN_MENU_IMAGE, caption=text, parse_mode="HTML"),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=get_service_menu()
                )
            except Exception:
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_service_menu(), parse_mode="HTML")
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=get_service_menu(), parse_mode="HTML")

    elif call.data.startswith("page_"):
        parts = call.data.split("_")
        service = parts[1]
        page = int(parts[2])
        s_name = SERVICES.get(service, {}).get("name", "Service")
        text = f"Selected: <b>{s_name}</b>\n\nNeeche se country choose karein ya search karein:"
        service_banner = SERVICE_IMAGES.get(service, MAIN_MENU_IMAGE)

        if call.message.photo:
            try:
                bot.edit_message_media(
                    media=InputMediaPhoto(service_banner, caption=text, parse_mode="HTML"),
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=get_countries_paged_menu(service, page)
                )
            except Exception:
                bot.edit_message_caption(caption=text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_countries_paged_menu(service, page), parse_mode="HTML")
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=get_countries_paged_menu(service, page), parse_mode="HTML")

    elif call.data == "menu_dep":
        bot.send_message(call.message.chat.id, "Deposit Amount select karein ya direct type karein (Minimum Rs 20):", reply_markup=get_deposit_menu())
        bot.answer_callback_query(call.id)
    elif call.data.startswith("setdep_"):
        amt = float(call.data.split("_")[1])
        send_payment_qr(call.message.chat.id, uid, amt, upi_choice=1)
        bot.answer_callback_query(call.id)
    elif call.data.startswith("toggle_upi_"):
        parts = call.data.split("_")
        target_upi = int(parts[2])
        amt = float(parts[3])
        send_payment_qr(call.message.chat.id, uid, amt, upi_choice=target_upi)
        bot.answer_callback_query(call.id, text=f"Switched to UPI {target_upi}")
    elif call.data.startswith("app_"):
        if uid not in ALL_ADMINS:
            return
        parts = call.data.split("_")
        target = int(parts[1])
        amt = float(parts[2])

        nb = update_bal(target, amt)
        msg = f"<b>Approved by Admin!</b>\nUser: <code>{target}</code> | Added: Rs {amt:.2f} | New Bal: Rs {nb:.2f}"

        if call.message.photo:
            bot.edit_message_caption(caption=msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text(text=msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")

        try:
            bot.send_message(target, f"<b>Payment Approved!</b>\nWallet me Rs {amt:.2f} add ho gaye hain.\nCurrent Balance: Rs {nb:.2f}", parse_mode="HTML")
        except Exception:
            pass

        _, ref_by = get_user(target)
        if ref_by and ref_by > 0:
            comm = round(amt * (REFER_COMMISSION_PERCENT / 100.0), 2)
            if comm > 0:
                rb = update_bal(ref_by, comm)
                try:
                    bot.send_message(ref_by, f"<b>Referral Commission!</b>\nReferral ne deposit kiya, 5% Commission (+Rs {comm}) mila!\nBalance: Rs {rb:.2f}", parse_mode="HTML")
                except Exception:
                    pass
    elif call.data.startswith("rej_"):
        if uid not in ALL_ADMINS:
            return
        tu = int(call.data.split("_")[1])
        m = f"Rejected by Admin! User: <code>{tu}</code>"
        if call.message.photo:
            bot.edit_message_caption(caption=m, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text(text=m, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        try:
            bot.send_message(tu, "Aapka deposit request reject kar diya gaya hai.")
        except Exception:
            pass
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        service = parts[1]
        code = parts[2]
        p = float(parts[3])
        s_name = SERVICES.get(service, {}).get("name", service.upper())

        country_data = next((c for c in CATALOG.get(service, []) if c["id"] == code), {"name": "Country", "flag": "🌐"})

        bal = get_bal(uid)
        if bal < p:
            bot.answer_callback_query(call.id, f"Balance kam hai! Price: Rs {p}, Bal: Rs {bal:.2f}", show_alert=True)
            return

        bot.answer_callback_query(call.id, f"Ordering {s_name}...")
        wait_msg = bot.send_message(call.message.chat.id, f"🔄 {country_data.get('flag')} {country_data.get('name')} {s_name} number manga rahe hain, kripya wait karein...")

        req_url = f"{BASE_URL}?api_key={SASTA_API_KEY}&action=getNumber&service={service}&country={code}&format=json"
        try:
            r = requests.get(req_url, timeout=10)
            res = r.json()
        except Exception:
            bot.edit_message_text("Connection error! Thodi der baad try karein.", chat_id=call.message.chat.id, message_id=wait_msg.message_id)
            return

        activation_id = res.get("activation_id") or res.get("id")
        phone = res.get("phone") or res.get("number")

        if not phone or not activation_id:
            err = res.get("error") or res.get("msg") or "Is country me filhal stock available nahi hai."
            bot.edit_message_text(f"❌ Failed: {err}", chat_id=call.message.chat.id, message_id=wait_msg.message_id)
            return

        update_bal(uid, -p)

        user_recent_orders[uid] = {
            "service": s_name,
            "country": f"{country_data.get('flag')} {country_data.get('name')}",
            "phone": phone,
            "status": "Waiting for OTP"
        }

        cancel_mk = InlineKeyboardMarkup()
        cancel_mk.add(InlineKeyboardButton("❌ Cancel Order & Refund", callback_data=f"cancel_order_{activation_id}_{p}"))

        order_text = (
            f"📱 <b>{s_name} Number Ready!</b>\n\n"
            f"Number: <code>+{phone}</code>\n"
            f"Country: {country_data.get('flag')} <b>{country_data.get('name')}</b>\n"
            f"Deducted: <b>Rs {p:.2f}</b>\n\n"
            f"⏳ <b>Waiting for OTP... (Timer: 20 Minutes)</b>\n"
            f"<i>Agar 20 minute me OTP nahi aata toh paisa automatically refund ho jayega.</i>"
        )
        status_msg = bot.send_message(call.message.chat.id, order_text, reply_markup=cancel_mk, parse_mode="HTML")

        threading.Thread(
            target=send_sale_receipt,
            args=(s_name, country_data.get("name"), country_data.get("flag"), phone, activation_id, p, uid, uname)
        ).start()

        threading.Thread(
            target=poll_otp_20_minutes,
            args=(call.message.chat.id, uid, activation_id, p, s_name, status_msg.message_id)
        ).start()

print(">> WORLDSIM HUB BOT RUNNING LIVE <<")
while True:
    try:
        bot.polling(none_stop=True, timeout=30, long_polling_timeout=30)
    except Exception as e:
        print(f"Connection retry error: {e}")
        time.sleep(3)
