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
BOT_TOKEN = "9109714291:AAFQny4eo62NZQy7TAnxXJQf3dG420gw2O4"
SASTA_API_KEY = "stp_4905928f4de82481bad70ffd7d8da6b59e82e625396bebc3"
BASE_URL = "https://sastasms.pro/stubs/handler_api.php"

DATABASE_URL = "postgresql://neondb_owner:npg_Hy4LqEYdOvk7@ep-weathered-river-bdjtcb91-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require"

MAIN_ADMIN = 8539777823           # @ub2_q
SECOND_ADMIN = 9013970075         # @Worldsim_hub
ALL_ADMINS = [MAIN_ADMIN, SECOND_ADMIN]

UPI_ID_1 = "alone..hacker@ybl"    # Primary UPI
UPI_ID_2 = "noname0011@axl"       # Backup UPI
MERCHANT_NAME = "WorldSIM Hub VIP"

SUPPORT_USERNAME = "@Worldsim_hub"
SUPPORT_LINK = "https://t.me/Worldsim_hub"

RECEIPT_CHANNEL_ID = -1004497033717
UPDATE_CHANNEL_ID  = -1004336033917

PROOFS_CHANNEL_LINK   = "https://t.me/+Qx7t_WPf2lNkOTY9"
OFFICIAL_CHANNEL_LINK = "https://t.me/+9PSAXiY4vBRlNjA1"

CHANNELS = [
    {"id": RECEIPT_CHANNEL_ID, "name": "🧾 Official Receipts & Proofs", "link": PROOFS_CHANNEL_LINK},
    {"id": UPDATE_CHANNEL_ID,  "name": "📢 WorldSIM Updates Channel",  "link": OFFICIAL_CHANNEL_LINK}
]

FORCE_JOIN_IMAGE = "https://placehold.co/1200x500/090d16/f59e0b.png?text=✦+WORLDSIM+HUB+VIP+✦%0AVerify+Channels+To+Unlock+Store&font=playfair-display"
MAIN_MENU_IMAGE  = "https://placehold.co/1200x500/090d16/fbbf24.png?text=✦+WORLDSIM+HUB+VIP+✦%0APremium+OTP+%26+Virtual+SIM+Store&font=playfair-display"
BROADCAST_IMAGE  = "https://placehold.co/1200x500/111827/f59e0b.png?text=✦+WORLDSIM+HUB+NOTICE+✦%0AOfficial+VIP+Announcement&font=playfair-display"

SERVICE_IMAGES = {
    "wa": "https://placehold.co/1200x500/022c22/34d399.png?text=✦+WORLDSIM+HUB+✦%0AWhatsApp+VIP+OTP+Servers&font=playfair-display",
    "tg": "https://placehold.co/1200x500/082f49/38bdf8.png?text=✦+WORLDSIM+HUB+✦%0ATelegram+VIP+OTP+Servers&font=playfair-display",
    "go": "https://placehold.co/1200x500/450a0a/fca5a5.png?text=✦+WORLDSIM+HUB+✦%0AGoogle+%2F+Gmail+VIP+OTP&font=playfair-display",
    "ig": "https://placehold.co/1200x500/3b0764/e879f9.png?text=✦+WORLDSIM+HUB+✦%0AInstagram+VIP+OTP+Servers&font=playfair-display",
    "fb": "https://placehold.co/1200x500/172554/93c5fd.png?text=✦+WORLDSIM+HUB+✦%0AFacebook+VIP+OTP+Servers&font=playfair-display"
}

PER_REFER_REWARD = 0.70
TELEGRAM_MARGIN_INR = 10.0
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
        {"id": "6",   "name": "Indonesia",      "flag": "🇮🇩", "price": 38.56},
        {"id": "34",  "name": "Chile",          "flag": "🇨🇱", "price": 44.21},
        {"id": "26",  "name": "Colombia",       "flag": "🇨🇴", "price": 46.00},
        {"id": "3",   "name": "China",          "flag": "🇨🇳", "price": 56.00},
        {"id": "36",  "name": "Canada",         "flag": "🇨🇦", "price": 65.00},
        {"id": "8",   "name": "Kenya",          "flag": "🇰🇪", "price": 66.90},
        {"id": "12",  "name": "USA",            "flag": "🇺🇸", "price": 70.00},
        {"id": "81",  "name": "Nepal",          "flag": "🇳🇵", "price": 73.40},
        {"id": "60",  "name": "Bangladesh",     "flag": "🇧🇩", "price": 75.32},
        {"id": "22",  "name": "India",          "flag": "🇮🇳", "price": 86.75},
        {"id": "16",  "name": "United Kingdom", "flag": "🇬🇧", "price": 140.00}
    ],
    "wa": [
        {"id": "6",   "name": "Indonesia",      "flag": "🇮🇩", "price": 30.00},
        {"id": "34",  "name": "Chile",          "flag": "🇨🇱", "price": 35.00},
        {"id": "12",  "name": "USA-2",          "flag": "🇺🇸", "price": 40.00},
        {"id": "26",  "name": "Colombia",       "flag": "🇨🇴", "price": 40.00},
        {"id": "107", "name": "South Africa",   "flag": "🇿🇦", "price": 50.00},
        {"id": "36",  "name": "Canada",         "flag": "🇨🇦", "price": 60.00},
        {"id": "66",  "name": "Pakistan",       "flag": "🇵🇰", "price": 70.00},
        {"id": "22",  "name": "India",          "flag": "🇮🇳", "price": 150.00}
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
user_dep_cache = {}
tg_live_price_cache = {"time": 0, "prices": {}}
BOT_USERNAME_CACHE = None

def get_telegram_live_catalog():
    now = time.time()
    if now - tg_live_price_cache["time"] < 300 and tg_live_price_cache["prices"]:
        return tg_live_price_cache["prices"]
    try:
        r = requests.get(f"{BASE_URL}?api_key={SASTA_API_KEY}&action=getPrices&service=tg", timeout=5)
        data = r.json()
        live_map = {}
        for cid, info in data.items():
            if isinstance(info, dict) and "tg" in info:
                raw_cost = float(info["tg"].get("cost", 0))
                if raw_cost > 0:
                    live_map[str(cid)] = round(raw_cost + TELEGRAM_MARGIN_INR, 2)
        if live_map:
            tg_live_price_cache["time"] = now
            tg_live_price_cache["prices"] = live_map
            return live_map
    except Exception:
        pass
    return {}

def get_service_catalog(service):
    items = [dict(c) for c in CATALOG.get(service, [])]
    if service == "tg":
        live_map = get_telegram_live_catalog()
        if live_map:
            for item in items:
                if item["id"] in live_map:
                    item["price"] = live_map[item["id"]]
    return items
# --- END OF PART 1 ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"WorldSIM Hub VIP Running 24/7!")
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
            CREATE TABLE IF NOT EXISTS worldsim_users (
                user_id BIGINT PRIMARY KEY,
                balance REAL DEFAULT 0.0,
                referred_by BIGINT DEFAULT 0,
                purchased_count INT DEFAULT 0,
                ref_paid BOOLEAN DEFAULT FALSE,
                pending_dep BOOLEAN DEFAULT FALSE
            );
            """)
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS purchased_count INT DEFAULT 0;")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS ref_paid BOOLEAN DEFAULT FALSE;")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS pending_dep BOOLEAN DEFAULT FALSE;")
        conn.commit()
    except Exception as e:
        print(f"Database Init Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

init_db()

def get_user(uid):
    uid = int(uid)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT balance, referred_by, COALESCE(purchased_count, 0) FROM worldsim_users WHERE user_id = %s;", (uid,))
            r = cur.fetchone()
            if r:
                return float(r[0]), int(r[1]), int(r[2])
            cur.execute("INSERT INTO worldsim_users (user_id, balance, referred_by, purchased_count, ref_paid, pending_dep) VALUES (%s, 0.0, 0, 0, FALSE, FALSE) ON CONFLICT DO NOTHING;", (uid,))
        conn.commit()
        return 0.0, 0, 0
    except Exception as e:
        print(f"get_user Error: {e}")
        return 0.0, 0, 0
    finally:
        if conn:
            release_db_conn(conn)

def get_bal(uid):
    bal, _, _ = get_user(uid)
    return bal

def has_pending_deposit(uid):
    uid = int(uid)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT COALESCE(pending_dep, FALSE) FROM worldsim_users WHERE user_id = %s;", (uid,))
            r = cur.fetchone()
            return bool(r[0]) if r else False
    except Exception:
        return False
    finally:
        if conn:
            release_db_conn(conn)

def set_pending_deposit(uid, status: bool):
    uid = int(uid)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO worldsim_users (user_id, balance, referred_by, purchased_count, ref_paid, pending_dep)
            VALUES (%s, 0.0, 0, 0, FALSE, %s)
            ON CONFLICT (user_id) DO UPDATE SET pending_dep = %s;
            """, (uid, status, status))
        conn.commit()
    except Exception as e:
        print(f"set_pending_deposit Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

def update_bal(uid, amt):
    uid = int(uid)
    amt = float(amt)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO worldsim_users (user_id, balance, referred_by, purchased_count, ref_paid, pending_dep) 
            VALUES (%s, GREATEST(0.0, %s), 0, 0, FALSE, FALSE)
            ON CONFLICT (user_id) 
            DO UPDATE SET balance = GREATEST(0.0, worldsim_users.balance + %s)
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
# --- END OF PART 2 ---
def increment_purchase_count(uid):
    uid = int(uid)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("UPDATE worldsim_users SET purchased_count = COALESCE(purchased_count, 0) + 1 WHERE user_id = %s;", (uid,))
        conn.commit()
    except Exception as e:
        print(f"increment_purchase Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

def set_referrer(uid, ref_id):
    uid = int(uid)
    ref_id = int(ref_id)
    if uid == ref_id:
        return
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT referred_by FROM worldsim_users WHERE user_id = %s;", (uid,))
            r = cur.fetchone()
            if not r:
                cur.execute("INSERT INTO worldsim_users (user_id, balance, referred_by, purchased_count, ref_paid, pending_dep) VALUES (%s, 0.0, %s, 0, FALSE, FALSE);", (uid, ref_id))
            elif r[0] == 0:
                cur.execute("UPDATE worldsim_users SET referred_by = %s WHERE user_id = %s;", (ref_id, uid))
        conn.commit()
    except Exception as e:
        print(f"set_referrer Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

def process_referral_reward(uid):
    uid = int(uid)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT referred_by, COALESCE(ref_paid, FALSE) FROM worldsim_users WHERE user_id = %s;", (uid,))
            r = cur.fetchone()
            if r and r[0] > 0 and not r[1]:
                ref_id = int(r[0])
                cur.execute("UPDATE worldsim_users SET ref_paid = TRUE WHERE user_id = %s;", (uid,))
                conn.commit()
                new_ref_bal = update_bal(ref_id, PER_REFER_REWARD)
                try:
                    bot.send_message(
                        ref_id,
                        f"🎁 <b>New VIP Referral Bonus!</b>\n\n"
                        f"Aapke link se ek naye member ne join kiya!\n"
                        f"💰 Reward Added: <b>+₹{PER_REFER_REWARD:.2f}</b>\n"
                        f"💳 New Balance: <b>₹{new_ref_bal:.2f}</b>",
                        parse_mode="HTML"
                    )
                except Exception:
                    pass
    except Exception as e:
        print(f"Referral reward error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

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
    mk.add(InlineKeyboardButton("✅ Verify & Unlock VIP Store", callback_data="check_join"))
    return mk

def send_force_join_prompt(chat_id):
    caption = (
        "╭━━━✦ <b>WORLDSIM HUB VIP</b> ✦━━━╮\n"
        "🔒 <b>Mandatory Channel Verification</b>\n\n"
        "Store unlock karne ke liye dono official channels join karein:\n\n"
        "1️⃣ <b>Official Receipts & Proofs</b>\n"
        "2️⃣ <b>WorldSIM Updates Channel</b>\n\n"
        "👇 <i>Join karne ke baad Verify button dabayein:</i>"
    )
    try:
        bot.send_photo(chat_id, photo=FORCE_JOIN_IMAGE, caption=caption, reply_markup=get_force_join_menu(), parse_mode="HTML")
    except Exception:
        bot.send_message(chat_id, caption, reply_markup=get_force_join_menu(), parse_mode="HTML")

def generate_dynamic_qr_url(upi_id, amount):
    note = f"WorldSIM_{int(time.time())}"
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
        "|   WORLDSIM HUB VIP • SALE RECEIPT    |\n"
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
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton("🛒 Buy Number", url=f"https://t.me/{get_bot_username()}?start=buy"))
    try:
        bot.send_message(RECEIPT_CHANNEL_ID, f"```\n{receipt}\n```", reply_markup=mk, parse_mode="Markdown")
    except Exception as e:
        print(f"Receipt channel post error: {e}")
# --- END OF PART 3 ---
def send_feedback_receipt_to_channel(buyer_id, stars, service_name, buyer_username):
    user_tag = format_user_tag(buyer_id, buyer_username)
    star_str = "⭐" * stars
    now_str = datetime.datetime.now().strftime("%d %b %Y  %H:%M")

    feedback_msg = (
        "+--------------------------------------+\n"
        "|   WORLDSIM HUB VIP • USER FEEDBACK   |\n"
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
    mk = InlineKeyboardMarkup()
    mk.add(InlineKeyboardButton("🛒 Buy Number", url=f"https://t.me/{get_bot_username()}?start=buy"))
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
    markup.add(InlineKeyboardButton("🛒 BROWSE VIP SERVICES", callback_data="open_browse_services"))
    markup.add(
        InlineKeyboardButton("💳 ADD BALANCE", callback_data="menu_dep"),
        InlineKeyboardButton("📦 MY ORDERS", callback_data="menu_orders")
    )
    markup.add(
        InlineKeyboardButton("👤 VIP PROFILE & REFER", callback_data="menu_profile"),
        InlineKeyboardButton("🛠️ 24/7 SUPPORT ↗", url=SUPPORT_LINK)
    )
    markup.add(
        InlineKeyboardButton("📢 UPDATES ↗", url=OFFICIAL_CHANNEL_LINK),
        InlineKeyboardButton("🧾 LIVE PROOFS ↗", url=PROOFS_CHANNEL_LINK)
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
    markup.add(InlineKeyboardButton("📘 Facebook OTP", callback_data="page_fb_0"))
    markup.add(InlineKeyboardButton("🏠 Back to VIP Home", callback_data="back_main"))
    return markup

def get_countries_paged_menu(service, page=0):
    markup = InlineKeyboardMarkup(row_width=2)
    country_list = get_service_catalog(service)
    start_idx = page * ITEMS_PER_PAGE
    end_idx = start_idx + ITEMS_PER_PAGE
    current_page_items = country_list[start_idx:end_idx]
    total_pages = (len(country_list) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    btns = []
    for c in current_page_items:
        cid = c["id"]
        price = c["price"]
        btn_text = f"{c['flag']} {c['name']} • ₹{price:g}"
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
        InlineKeyboardButton("₹20", callback_data="setdep_20"),
        InlineKeyboardButton("₹50", callback_data="setdep_50"),
        InlineKeyboardButton("₹100", callback_data="setdep_100"),
        InlineKeyboardButton("₹200", callback_data="setdep_200")
    )
    mk.add(InlineKeyboardButton("🏠 Back to VIP Home", callback_data="back_main"))
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
    if has_pending_deposit(uid):
        bot.send_message(
            chat_id,
            "⏳ <b>Aapka ek payment screenshot pehle se verification ke liye pending hai!</b>\n\n"
            "Ek baar me sirf <b>1 payment request</b> hi bhej sakte hain. Admin approval ke baad hi naya payment karein.",
            parse_mode="HTML"
        )
        return

    chosen_upi = UPI_ID_1 if upi_choice == 1 else UPI_ID_2
    user_dep_cache[uid] = {"amt": amount, "upi": upi_choice}
    qr_url = generate_dynamic_qr_url(chosen_upi, amount)

    caption = (
        f"╭━━━✦ <b>VIP PAYMENT GATEWAY</b> ✦━━━╮\n"
        f"💳 <b>Deposit Amount:</b> ₹{amount:.2f}\n\n"
        f"📲 <b>UPI ID:</b> <code>{chosen_upi}</code>\n"
        f"🛠️ <b>Support:</b> {SUPPORT_USERNAME}\n\n"
        f"⚠️ <b>Important:</b> Payment karne ke baad <b>sirf 1 baar Screenshot</b> bhejein. Approval se pehle dobara photo send nahi hogi."
    )
    bot.send_photo(chat_id, qr_url, caption=caption, reply_markup=get_qr_toggle_menu(upi_choice, amount), parse_mode="HTML")

def poll_otp_20_minutes(cid, uid, activation_id, price, service_name, status_msg_id):
    active_orders[activation_id] = {"status": "waiting"}
    status_url = f"{BASE_URL}?api_key={SASTA_API_KEY}&action=getStatus&id={activation_id}"
    cancel_url = f"{BASE_URL}?api_key={SASTA_API_KEY}&action=setStatus&status=8&id={activation_id}"
    
    for check in range(300):
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
                    bot.send_message(cid, f"✅ <b>Aapka VIP OTP Code:</b> <code>{otp}</code>", parse_mode="HTML")
                    time.sleep(1)
                    bot.send_message(cid, f"🌟 <b>Order Complete!</b>\n\nAapko hamari <b>{service_name}</b> service kaisi lagi? Rate karein:", reply_markup=get_feedback_menu(service_name), parse_mode="HTML")
                    if activation_id in active_orders:
                        del active_orders[activation_id]
                    return
            elif "STATUS_CANCEL" in text_res:
                new_bal = update_bal(uid, price)
                bot.send_message(cid, f"❌ Order server dwara cancel kar diya gaya.\n<b>₹{price:.2f} refund kar diye gaye hain!</b>\nWallet Balance: <b>₹{new_bal:.2f}</b>", parse_mode="HTML")
                if activation_id in active_orders:
                    del active_orders[activation_id]
                return
            else:
                try:
                    res = r.json()
                    if res.get("status") == "STATUS_OK" or "code" in res:
                        otp = res.get("code") or res.get("sms")
                        if otp and str(otp).lower() != "none":
                            bot.send_message(cid, f"✅ <b>Aapka VIP OTP Code:</b> <code>{otp}</code>", parse_mode="HTML")
                            time.sleep(1)
                            bot.send_message(cid, f"🌟 <b>Order Complete!</b>\n\nAapko hamari <b>{service_name}</b> service kaisi lagi? Rate karein:", reply_markup=get_feedback_menu(service_name), parse_mode="HTML")
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
    bot.send_message(cid, f"⏳ <b>20 Minute Timeout!</b>\n\n20 minute me OTP receive nahi hua. Order cancel kar diya gaya hai.\n\n💰 <b>Refund:</b> ₹{price:.2f} wallet me wapas add ho gaye hain.\nCurrent Balance: <b>₹{new_bal:.2f}</b>", parse_mode="HTML")
# --- END OF PART 4 ---
@bot.message_handler(commands=["list", "users", "userlist"])
def admin_users_list(m):
    if m.from_user.id not in ALL_ADMINS:
        return
    conn = None
    rows = []
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, balance, COALESCE(purchased_count, 0) FROM worldsim_users ORDER BY balance DESC, purchased_count DESC;")
            rows = cur.fetchall()
    except Exception as e:
        bot.reply_to(m, f"DB Error: {e}")
        return
    finally:
        if conn:
            release_db_conn(conn)

    if not rows:
        bot.reply_to(m, "Abhi tak koi user registered nahi hai.")
        return

    header = (
        f"╭━━━✦ <b>WORLDSIM HUB USER LIST</b> ✦━━━╮\n"
        f"👥 <b>Total Users:</b> {len(rows)}\n"
        f"💰 <b>Total Wallet Bal:</b> ₹{sum(float(r[1]) for r in rows):.2f}\n"
        f"🛒 <b>Total Accounts Bought:</b> {sum(int(r[2]) for r in rows)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    chunk = header
    for idx, r in enumerate(rows, 1):
        line = f"{idx}. <code>{r[0]}</code> | Bal: <b>₹{float(r[1]):.2f}</b> | Buys: <b>{int(r[2])}</b>\n"
        if len(chunk) + len(line) > 3800:
            bot.send_message(m.chat.id, chunk, parse_mode="HTML")
            chunk = ""
        chunk += line
    if chunk:
        bot.send_message(m.chat.id, chunk, parse_mode="HTML")

@bot.message_handler(commands=["addbalance", "addbal", "givebal"])
def admin_add_balance(m):
    if m.from_user.id not in ALL_ADMINS:
        return
    parts = m.text.split()
    if len(parts) < 3:
        bot.reply_to(m, "Format: <code>/addbalance <user_id> <amount></code>", parse_mode="HTML")
        return
    try:
        target_uid, amount = int(parts[1]), float(parts[2])
    except ValueError:
        bot.reply_to(m, "User ID aur Amount sahi numbers hone chahiye!")
        return
    if amount <= 0:
        return
    new_bal = update_bal(target_uid, amount)
    set_pending_deposit(target_uid, False)
    bot.reply_to(m, f"✅ Added ₹{amount:.2f} to <code>{target_uid}</code>\nNaya Balance: ₹{new_bal:.2f}", parse_mode="HTML")
    try:
        bot.send_message(target_uid, f"🎉 <b>Wallet me ₹{amount:.2f} add ho gaye hain!</b>\nBalance: <b>₹{new_bal:.2f}</b>", parse_mode="HTML")
    except Exception:
        pass

@bot.message_handler(commands=["checkbalance", "checkbal", "userbal"])
def admin_check_user_balance(m):
    if m.from_user.id not in ALL_ADMINS:
        return
    parts = m.text.split()
    if len(parts) < 2:
        bot.reply_to(m, "Format: <code>/checkbalance <user_id></code>", parse_mode="HTML")
        return
    try:
        target_uid = int(parts[1])
    except ValueError:
        return
    user_bal, ref_by, buys = get_user(target_uid)
    bot.reply_to(m, f"👤 <b>VIP User Details:</b>\n\n• <b>User ID:</b> <code>{target_uid}</code>\n• <b>Balance:</b> <b>₹{user_bal:.2f}</b>\n• <b>Accounts Bought:</b> <b>{buys}</b>\n• <b>Referred By:</b> <code>{ref_by if ref_by != 0 else 'None'}</code>", parse_mode="HTML")

@bot.message_handler(commands=["cutbalance", "cutbal", "removebal", "deductbal"])
def admin_cut_balance(m):
    if m.from_user.id not in ALL_ADMINS:
        return
    parts = m.text.split()
    if len(parts) < 3:
        bot.reply_to(m, "Format: <code>/cutbalance <user_id> <amount></code>", parse_mode="HTML")
        return
    try:
        target_uid, amount = int(parts[1]), float(parts[2])
    except ValueError:
        return
    if amount <= 0:
        return
    new_bal = update_bal(target_uid, -amount)
    bot.reply_to(m, f"✂️ Deducted ₹{amount:.2f} from <code>{target_uid}</code>\nRemaining Balance: <b>₹{new_bal:.2f}</b>", parse_mode="HTML")

@bot.message_handler(commands=["broadcast", "sendall", "update", "botupdate"])
def broadcast_message(m):
    if m.from_user.id not in ALL_ADMINS:
        return
    msg_text = m.text.split(" ", 1)[1].strip() if " " in m.text else "🚀 WorldSIM Hub VIP naye saste rates live ho chuke hain!"
    conn = None
    all_users = []
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM worldsim_users;")
            all_users = cur.fetchall()
    finally:
        if conn:
            release_db_conn(conn)
    sent = 0
    for user in all_users:
        try:
            bot.send_photo(user[0], photo=BROADCAST_IMAGE, caption=f"📢 <b>WorldSIM Hub VIP Notice:</b>\n\n{msg_text}", parse_mode="HTML")
            sent += 1
            time.sleep(0.05)
        except Exception:
            pass
    bot.send_message(m.chat.id, f"✅ Broadcast Complete! Delivered: <b>{sent}</b>", parse_mode="HTML")

def build_vip_home_text(name, uid, bal, buys):
    return (
        f"╭━━━✦ <b>WORLDSIM HUB VIP</b> ✦━━━╮\n\n"
        f"👤 <b>Member:</b> {name}\n"
        f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
        f"💰 <b>Wallet Balance:</b> ₹{bal:.2f}\n"
        f"📦 <b>Accounts Bought:</b> {buys}\n"
        f"🎁 <b>Refer & Earn:</b> ₹{PER_REFER_REWARD:.2f} / Refer\n\n"
        f"<i>Select an option from the VIP menu below:</i>"
    )

@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id
    name = m.from_user.first_name or "VIP User"
    parts = m.text.split()
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            set_referrer(uid, int(parts[1].replace("ref_", "")))
        except Exception:
            pass
    if not is_user_member(uid):
        send_force_join_prompt(m.chat.id)
        return
    bal, _, buys = get_user(uid)
    process_referral_reward(uid)
    if len(parts) > 1 and parts[1] == "buy":
        text = "╭━━━✦ <b>VIP OTP SERVICES</b> ✦━━━╮\n\nApni pasandida service select karein:"
        bot.send_photo(m.chat.id, photo=MAIN_MENU_IMAGE, caption=text, reply_markup=get_service_picker_menu(), parse_mode="HTML")
        return
    text = build_vip_home_text(name, uid, bal, buys)
    try:
        bot.send_photo(m.chat.id, photo=MAIN_MENU_IMAGE, caption=text, reply_markup=get_service_menu(), parse_mode="HTML")
    except Exception:
        bot.reply_to(m, text, reply_markup=get_service_menu(), parse_mode="HTML")

@bot.message_handler(func=lambda m: not m.text.startswith("/"))
def text_flow(m):
    uid = m.from_user.id
    if not is_user_member(uid):
        send_force_join_prompt(m.chat.id)
        return
    raw = m.text.strip()
    if uid in user_search_state:
        service = user_search_state.pop(uid)
        matches = [c for c in get_service_catalog(service) if raw.lower() in c["name"].lower()]
        if not matches:
            bot.reply_to(m, f"❌ '<b>{raw}</b>' naam ka koi country nahi mila!", reply_markup=get_service_menu(), parse_mode="HTML")
            return
        mk = InlineKeyboardMarkup(row_width=2)
        btns = [InlineKeyboardButton(f"{c['flag']} {c['name']} • ₹{c['price']:g}", callback_data=f"buy_{service}_{c['id']}_{c['price']}") for c in matches]
        for i in range(0, len(btns), 2):
            mk.row(*btns[i:i+2])
        mk.add(InlineKeyboardButton("🔙 Back to Services", callback_data="open_browse_services"))
        bot.reply_to(m, f"🔍 <b>Search Results for '{raw}':</b>", reply_markup=mk, parse_mode="HTML")
        return
    if raw.isdigit() and len(raw) <= 5:
        amt = float(raw)
        if amt < 20:
            bot.reply_to(m, "⚠️ <b>Minimum deposit ₹20 hai!</b>", parse_mode="HTML")
            return
        send_payment_qr(m.chat.id, uid, amt, upi_choice=1)
        return
    bot.reply_to(m, "⚠️ <b>Kripya Payment ka Screenshot send karein!</b>", parse_mode="HTML")

@bot.message_handler(content_types=['photo'])
def photo_flow(m):
    uid = m.from_user.id
    if not is_user_member(uid):
        send_force_join_prompt(m.chat.id)
        return

    if has_pending_deposit(uid):
        bot.reply_to(
            m,
            "⏳ <b>Aapka ek payment screenshot pehle se pending hai!</b>\n\n"
            "Ek baar me sirf <b>1 hi screenshot</b> bheja ja sakta hai. Admin approval ke baad hi dobara request bhejein.",
            parse_mode="HTML"
        )
        return

    set_pending_deposit(uid, True)
    amt = user_dep_cache.get(uid, {"amt": 20.0})["amt"]
    cap = m.caption if m.caption else "No Caption"
    name = m.from_user.first_name or "User"
    user_tag = format_user_tag(uid, m.from_user.username)

    mk = InlineKeyboardMarkup()
    mk.row(
        InlineKeyboardButton(f"✅ Approve ₹{int(amt)}", callback_data=f"app_{uid}_{amt}_photo"),
        InlineKeyboardButton("❌ Reject", callback_data=f"rej_{uid}")
    )
    admin_cap = (
        f"<b>Naya VIP Deposit Screenshot (Single Request)!</b>\n"
        f"User: <b>{name}</b> ({user_tag} | <code>{uid}</code>)\n"
        f"Amount: <b>₹{amt:.2f}</b>\n"
        f"Caption: <code>{cap}</code>"
    )
    for admin in ALL_ADMINS:
        try:
            bot.send_photo(admin, m.photo[-1].file_id, caption=admin_cap, reply_markup=mk, parse_mode="HTML")
        except Exception:
            pass
    bot.reply_to(m, f"✅ <b>Screenshot submit ho gaya!</b>\n\nAb admin ke approve/reject karne tak wait karein (dobara photo send karne ki zaroorat nahi hai).\nSupport: {SUPPORT_USERNAME}", parse_mode="HTML")

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid = call.from_user.id
    uname = call.from_user.username

    if call.data == "check_join":
        unjoined = get_user_unjoined_channels(uid)
        if not unjoined:
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            bal, _, buys = get_user(uid)
            process_referral_reward(uid)
            text = "✅ <b>VIP Access Unlocked!</b>\n\n" + build_vip_home_text(call.from_user.first_name or "VIP User", uid, bal, buys)
            bot.send_photo(call.message.chat.id, photo=MAIN_MENU_IMAGE, caption=text, reply_markup=get_service_menu(), parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, f"⚠️ Abhi {len(unjoined)} channel(s) baaki hain!", show_alert=True)
        return

    if call.data == "menu_profile":
        bal, _, buys = get_user(uid)
        ref_link = f"https://t.me/{get_bot_username()}?start=ref_{uid}"
        conn = None
        refs = 0
        try:
            conn = get_db_conn()
            with conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM worldsim_users WHERE referred_by = %s;", (uid,))
                refs = cur.fetchone()[0]
        finally:
            if conn:
                release_db_conn(conn)
        prof_text = (
            f"╭━━━✦ <b>VIP PROFILE & REFERRALS</b> ✦━━━╮\n\n"
            f"🆔 <b>User ID:</b> <code>{uid}</code>\n"
            f"💰 <b>Wallet Balance:</b> ₹{bal:.2f}\n"
            f"📦 <b>Accounts Bought:</b> {buys}\n"
            f"👥 <b>Total Referrals:</b> {refs} Users\n"
            f"🎁 <b>Referral Earnings:</b> ₹{round(refs * PER_REFER_REWARD, 2):.2f} (₹{PER_REFER_REWARD:.2f}/refer)\n\n"
            f"🔗 <b>Your Referral Link:</b>\n<code>{ref_link}</code>"
        )
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("💳 Add Balance", callback_data="menu_dep"))
        mk.add(InlineKeyboardButton("🏠 Back to VIP Home", callback_data="back_main"))
        bot.send_photo(call.message.chat.id, photo=MAIN_MENU_IMAGE, caption=prof_text, reply_markup=mk, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if call.data == "menu_orders":
        last_ord = user_recent_orders.get(uid)
        ord_text = "📦 <b>Aapka koi active order nahi hai.</b>" if not last_ord else f"╭━━━✦ <b>RECENT VIP ORDER</b> ✦━━━╮\n\n• <b>Service:</b> {last_ord.get('service')}\n• <b>Country:</b> {last_ord.get('country')}\n• <b>Number:</b> <code>+{last_ord.get('phone')}</code>\n• <b>Status:</b> {last_ord.get('status')}"
        mk = InlineKeyboardMarkup()
        mk.add(InlineKeyboardButton("🛒 Browse VIP Services", callback_data="open_browse_services"))
        mk.add(InlineKeyboardButton("🏠 Back to VIP Home", callback_data="back_main"))
        bot.send_photo(call.message.chat.id, photo=MAIN_MENU_IMAGE, caption=ord_text, reply_markup=mk, parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if call.data == "open_browse_services":
        text = "╭━━━✦ <b>VIP OTP SERVICES</b> ✦━━━╮\n\nApni pasandida service select karein:"
        if call.message.photo:
            bot.edit_message_media(media=InputMediaPhoto(MAIN_MENU_IMAGE, caption=text, parse_mode="HTML"), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_service_picker_menu())
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=get_service_picker_menu(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
        return

    if call.data.startswith("search_country_"):
        user_search_state[uid] = call.data.replace("search_country_", "")
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🔍 <b>Country ka naam type karein:</b>", parse_mode="HTML")
        return

    if call.data.startswith("rate_"):
        parts = call.data.split("_")
        stars = int(parts[1])
        s_name = parts[2] if len(parts) > 2 else "OTP Service"
        bot.answer_callback_query(call.id, f"Aapne {stars} Star diya!")
        bot.edit_message_text(text=f"💖 <b>Feedback ke liye shukriya!</b> ({'⭐' * stars})", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        threading.Thread(target=send_feedback_receipt_to_channel, args=(uid, stars, s_name, uname)).start()
        return

    if call.data.startswith("cancel_order_"):
        parts = call.data.split("_")
        act_id, refund_price = parts[2], float(parts[3])
        if act_id in active_orders:
            active_orders[act_id]["status"] = "cancelled_by_user"
        try:
            requests.get(f"{BASE_URL}?api_key={SASTA_API_KEY}&action=setStatus&status=8&id={act_id}", timeout=5)
        except Exception:
            pass
        new_bal = update_bal(uid, refund_price)
        bot.answer_callback_query(call.id, "Order cancelled! Amount refunded.")
        bot.edit_message_text(f"❌ <b>Order Cancelled!</b>\n\n₹{refund_price:.2f} refund ho gaye hain.\nBalance: <b>₹{new_bal:.2f}</b>", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        return

    if not is_user_member(uid) and uid not in ALL_ADMINS:
        bot.answer_callback_query(call.id, "⚠️ Pehle dono channels join karein!", show_alert=True)
        return

    bal, _, buys = get_user(uid)

    if call.data == "ignore":
        bot.answer_callback_query(call.id)
    elif call.data == "back_main":
        text = build_vip_home_text(call.from_user.first_name or "VIP User", uid, bal, buys)
        if call.message.photo:
            bot.edit_message_media(media=InputMediaPhoto(MAIN_MENU_IMAGE, caption=text, parse_mode="HTML"), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_service_menu())
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=get_service_menu(), parse_mode="HTML")
    elif call.data.startswith("page_"):
        parts = call.data.split("_")
        service, page = parts[1], int(parts[2])
        s_name = SERVICES.get(service, {}).get("name", "Service")
        text = f"✦ <b>{s_name} VIP Servers</b> ✦\n\nNeeche se country choose karein:"
        if call.message.photo:
            bot.edit_message_media(media=InputMediaPhoto(SERVICE_IMAGES.get(service, MAIN_MENU_IMAGE), caption=text, parse_mode="HTML"), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_countries_paged_menu(service, page))
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=text, reply_markup=get_countries_paged_menu(service, page), parse_mode="HTML")
    elif call.data == "menu_dep":
        if has_pending_deposit(uid):
            bot.answer_callback_query(call.id, "⏳ Aapka ek screenshot pehle se pending hai! Approval ka wait karein.", show_alert=True)
            return
        bot.send_photo(call.message.chat.id, photo=MAIN_MENU_IMAGE, caption="💳 <b>Deposit Amount select karein ya direct type karein (Minimum ₹20):</b>", reply_markup=get_deposit_menu(), parse_mode="HTML")
        bot.answer_callback_query(call.id)
    elif call.data.startswith("setdep_"):
        send_payment_qr(call.message.chat.id, uid, float(call.data.split("_")[1]), upi_choice=1)
        bot.answer_callback_query(call.id)
    elif call.data.startswith("toggle_upi_"):
        parts = call.data.split("_")
        send_payment_qr(call.message.chat.id, uid, float(parts[3]), upi_choice=int(parts[2]))
        bot.answer_callback_query(call.id)
    elif call.data.startswith("app_"):
        if uid not in ALL_ADMINS:
            return
        parts = call.data.split("_")
        target, amt = int(parts[1]), float(parts[2])
        nb = update_bal(target, amt)
        set_pending_deposit(target, False)
        msg = f"✅ <b>Approved by Admin!</b>\nUser: <code>{target}</code> | Added: ₹{amt:.2f} | New Bal: ₹{nb:.2f}"
        if call.message.photo:
            bot.edit_message_caption(caption=msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text(text=msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        try:
            bot.send_message(target, f"🎉 <b>Payment Approved!</b>\nWallet me ₹{amt:.2f} add ho gaye hain.\nCurrent Balance: ₹{nb:.2f}", parse_mode="HTML")
        except Exception:
            pass
    elif call.data.startswith("rej_"):
        if uid not in ALL_ADMINS:
            return
        tu = int(call.data.split("_")[1])
        set_pending_deposit(tu, False)
        m = f"❌ Rejected by Admin! User: <code>{tu}</code>"
        if call.message.photo:
            bot.edit_message_caption(caption=m, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        else:
            bot.edit_message_text(text=m, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        try:
            bot.send_message(tu, "❌ Aapka deposit request reject kar diya gaya hai. Ab aap sahi screenshot dobara bhej sakte hain.")
        except Exception:
            pass
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        service, code, p = parts[1], parts[2], float(parts[3])
        s_name = SERVICES.get(service, {}).get("name", service.upper())
        country_data = next((c for c in get_service_catalog(service) if c["id"] == code), {"name": "Country", "flag": "🌐"})
        if get_bal(uid) < p:
            bot.answer_callback_query(call.id, f"Balance kam hai! Price: ₹{p}, Bal: ₹{get_bal(uid):.2f}", show_alert=True)
            return
        bot.answer_callback_query(call.id, f"Ordering {s_name}...")
        wait_msg = bot.send_message(call.message.chat.id, f"🔄 {country_data.get('flag')} {country_data.get('name')} {s_name} VIP number manga rahe hain...")
        try:
            res = requests.get(f"{BASE_URL}?api_key={SASTA_API_KEY}&action=getNumber&service={service}&country={code}&format=json", timeout=10).json()
        except Exception:
            bot.edit_message_text("Connection error!", chat_id=call.message.chat.id, message_id=wait_msg.message_id)
            return
        activation_id = res.get("activation_id") or res.get("id")
        phone = res.get("phone") or res.get("number")
        if not phone or not activation_id:
            bot.edit_message_text(f"❌ Failed: {res.get('error') or res.get('msg') or 'Stock unavailable'}", chat_id=call.message.chat.id, message_id=wait_msg.message_id)
            return
        update_bal(uid, -p)
        increment_purchase_count(uid)
        user_recent_orders[uid] = {"service": s_name, "country": f"{country_data.get('flag')} {country_data.get('name')}", "phone": phone, "status": "Waiting for OTP"}
        cancel_mk = InlineKeyboardMarkup()
        cancel_mk.add(InlineKeyboardButton("❌ Cancel Order & Refund", callback_data=f"cancel_order_{activation_id}_{p}"))
        order_text = (
            f"╭━━━✦ <b>{s_name.upper()} VIP NUMBER</b> ✦━━━╮\n\n"
            f"📱 <b>Number:</b> <code>+{phone}</code>\n"
            f"🌍 <b>Country:</b> {country_data.get('flag')} <b>{country_data.get('name')}</b>\n"
            f"💸 <b>Deducted:</b> ₹{p:.2f}\n\n"
            f"⏳ <b>Waiting for OTP... (Timer: 20 Minutes)</b>"
        )
        status_msg = bot.send_message(call.message.chat.id, order_text, reply_markup=cancel_mk, parse_mode="HTML")
        threading.Thread(target=send_sale_receipt, args=(s_name, country_data.get("name"), country_data.get("flag"), phone, activation_id, p, uid, uname)).start()
        threading.Thread(target=poll_otp_20_minutes, args=(call.message.chat.id, uid, activation_id, p, s_name, status_msg.message_id)).start()

print(">> WORLDSIM HUB VIP BOT RUNNING LIVE <<")
while True:
    try:
        bot.polling(none_stop=True, timeout=30, long_polling_timeout=30)
    except Exception as e:
        print(f"Connection retry error: {e}")
        time.sleep(3)
# --- END OF PART 5 ---
                    
