import os
import re
import uuid
import time
import datetime
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import psycopg2
from psycopg2 import pool

# ================= CONFIGURATION =================
BOT_TOKEN = "9109714291:AAFQny4eo62NZQy7TAnxXJQf3dG420gw2O4"
SASTA_API_KEY = "stp_4905928f4de82481bad70ffd7d8da6b59e82e625396bebc3"
BASE_URL = "https://sastasms.pro/stubs/handler_api.php"

ZAPUPI_API_KEY = "zap81dd07798ad86781b13f7e7e632d1486"
ZAPUPI_FEE_PERCENT = 2.0
MERCHANT_UPI_ID = "paytm.s4qvafn@pty"
MERCHANT_NAME = "WorldSIM Hub"

DATABASE_URL = "postgresql://neondb_owner:npg_Hy4LqEYdOvk7@ep-weathered-river-bdjtcb91-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require"

MAIN_ADMIN = 8539777823           # @ub2_q
SECOND_ADMIN = 9013970075         # @Worldsim_hub
ALL_ADMINS = [MAIN_ADMIN, SECOND_ADMIN]

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
user_input_state = {}
pending_zap_orders = {}
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

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"WorldSIM Hub Running 24/7!")
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
                pending_dep BOOLEAN DEFAULT FALSE,
                username TEXT DEFAULT '',
                nickname TEXT DEFAULT ''
            );
            """)
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS purchased_count INT DEFAULT 0;")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS ref_paid BOOLEAN DEFAULT FALSE;")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS pending_dep BOOLEAN DEFAULT FALSE;")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS username TEXT DEFAULT '';")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS nickname TEXT DEFAULT '';")
            cur.execute("""
            CREATE TABLE IF NOT EXISTS used_utrs (
                utr TEXT PRIMARY KEY,
                user_id BIGINT,
                amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS verified_orders (
                order_id TEXT PRIMARY KEY,
                user_id BIGINT,
                utr TEXT,
                amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)
        conn.commit()
    except Exception as e:
        print(f"Database Init Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

init_db()

def sync_user_info(uid, username, nickname):
    uid = int(uid)
    uname = f"@{username.replace('@', '')}" if username else ""
    nick = (nickname or "User").strip()
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("""
            INSERT INTO worldsim_users (user_id, balance, referred_by, purchased_count, ref_paid, pending_dep, username, nickname)
            VALUES (%s, 0.0, 0, 0, FALSE, FALSE, %s, %s)
            ON CONFLICT (user_id) DO UPDATE SET username = %s, nickname = %s;
            """, (uid, uname, nick, uname, nick))
        conn.commit()
    except Exception as e:
        print(f"sync_user_info Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

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

def is_utr_or_order_used(utr, order_id):
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM used_utrs WHERE utr = %s;", (utr,))
            if cur.fetchone():
                return True
            cur.execute("SELECT 1 FROM verified_orders WHERE order_id = %s;", (order_id,))
            if cur.fetchone():
                return True
        return False
    except Exception:
        return True
    finally:
        if conn:
            release_db_conn(conn)

def mark_utr_and_order_used(utr, order_id, uid, amount):
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO used_utrs (utr, user_id, amount) VALUES (%s, %s, %s);", (utr, int(uid), float(amount)))
            cur.execute("INSERT INTO verified_orders (order_id, user_id, utr, amount) VALUES (%s, %s, %s, %s);", (order_id, int(uid), utr, float(amount)))
        conn.commit()
        return True
    except Exception as e:
        print(f"mark_utr_and_order_used Error: {e}")
        return False
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
                        f"🎁 <b>New Referral Bonus!</b>\n\n"
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
    mk.add(InlineKeyboardButton("✅ Verify & Unlock Store", callback_data="check_join"))
    return mk

def send_force_join_prompt(chat_id):
    text = (
        "<blockquote>"
        "🔒 <b>Mandatory Channel Verification</b>\n"
        "Store unlock karne ke liye dono official channels join karein:\n\n"
        "1️⃣ <b>Official Receipts & Proofs</b>\n"
        "2️⃣ <b>WorldSIM Updates Channel</b>"
        "</blockquote>\n\n"
        "👇 <i>Join karne ke baad Verify button dabayein:</i>"
    )
    bot.send_message(chat_id, text, reply_markup=get_force_join_menu(), parse_mode="HTML")

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
        f"|  Status     : OTP DELIVERED OK       |\n"
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
    mk.add(InlineKeyboardButton("🛒 Buy Account", url=f"https://t.me/{get_bot_username()}?start=buy"))
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
    mk.add(InlineKeyboardButton("🛒 Buy Account", url=f"https://t.me/{get_bot_username()}?start=buy"))
    try:
        bot.send_message(RECEIPT_CHANNEL_ID, f"```\n{feedback_msg}\n```", reply_markup=mk, parse_mode="Markdown")
    except Exception as e:
        print(f"Feedback error: {e}")

def create_zapupi_order(uid, amount):
    order_id = f"{int(time.time())}{str(uid)[-4:]}"
    fee = round(amount * (ZAPUPI_FEE_PERCENT / 100.0), 2)
    net_credit = round(amount - fee, 2)
    pay_note = f"WorldSIM{order_id[-6:]}"

    payment_url = None
    upi_intent_str = None
    api_err = ""

    try:
        payload = {
            "zap_key": ZAPUPI_API_KEY,
            "order_id": order_id,
            "amount": str(int(amount) if float(amount).is_integer() else amount),
            "customer_mobile": "9876543210",
            "remark": pay_note
        }
        headers = {"Content-Type": "application/json"}
        resp = requests.post("https://pay.zapupi.com/api/create-order", json=payload, headers=headers, timeout=10)
        data = resp.json()
        if str(data.get("status", "")).lower() == "success":
            payment_url = data.get("payment_url")
            upi_intent_str = data.get("upi_intent") or data.get("upi_link") or payment_url
        else:
            api_err = f"\n⚠️ <i>Gateway Error: {data.get('message', resp.text[:80])}</i>"
    except Exception as e:
        api_err = f"\n⚠️ <i>API Error: {str(e)[:60]}</i>"

    if not payment_url:
        return None, None, api_err

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=350x350&data={urllib.parse.quote(upi_intent_str)}"

    order_obj = {
        "order_id": order_id,
        "amount": amount,
        "fee": fee,
        "net_credit": net_credit,
        "pay_note": pay_note,
        "payment_url": payment_url,
        "created_at": time.time()
    }
    pending_zap_orders[uid] = order_obj
    return order_obj, qr_url, ""

def verify_zapupi_utr(order_id, utr):
    try:
        payload = {
            "zap_key": ZAPUPI_API_KEY,
            "order_id": order_id
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post("https://pay.zapupi.com/api/order-status", json=payload, headers=headers, timeout=10)
        data = r.json()
        status_val = str(data.get("status", "")).lower()
        data_obj = data.get("data") if isinstance(data.get("data"), dict) else {}
        txn_status = str(data_obj.get("status", "")).lower()

        if status_val in ["success", "paid", "completed"] or txn_status in ["success", "paid", "completed"]:
            api_utr = str(data.get("utr") or data_obj.get("utr") or "").strip()
            if api_utr and api_utr != utr:
                return False, "UTR is order se match nahi hua!"
            return True, "Verified"

        return False, data.get("message", "Abhi payment complete nahi dikh raha")
    except Exception as e:
        print(f"Payment verify error: {e}")
    return False, "Payment server connection error"

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

def build_home_text(name, uid, bal):
    return (
        "<blockquote>"
        f"✨ <b>Welcome, {name}!</b>\n"
        f"🪪 <b>ID:</b> <code>{uid}</code>\n"
        f"💲 <b>Wallet:</b> ₹{bal:.2f}\n"
        f"🔒 Secure  ·  ✉️ Instant OTP"
        "</blockquote>"
    )

def get_home_menu():
    mk = InlineKeyboardMarkup(row_width=2)
    mk.add(InlineKeyboardButton("🛒 Buy Account", callback_data="open_browse_services"))
    mk.add(
        InlineKeyboardButton("📑 My Orders", callback_data="menu_orders"),
        InlineKeyboardButton("👤 Profile", callback_data="menu_profile")
    )
    mk.add(
        InlineKeyboardButton("💲 Recharge", callback_data="menu_dep"),
        InlineKeyboardButton("🎁 Refer & Earn", callback_data="menu_refer")
    )
    mk.add(InlineKeyboardButton("🛠️ Support", url=SUPPORT_LINK))
    mk.add(InlineKeyboardButton("📋 Terms & Conditions", callback_data="menu_terms"))
    return mk

def get_service_picker_menu():
    mk = InlineKeyboardMarkup(row_width=2)
    mk.add(
        InlineKeyboardButton("✈️ Telegram OTP", callback_data="page_tg_0"),
        InlineKeyboardButton("💬 WhatsApp OTP", callback_data="page_wa_0")
    )
    mk.add(
        InlineKeyboardButton("🌐 Google/Gmail OTP", callback_data="page_go_0"),
        InlineKeyboardButton("📸 Instagram OTP", callback_data="page_ig_0")
    )
    mk.add(InlineKeyboardButton("📘 Facebook OTP", callback_data="page_fb_0"))
    mk.add(InlineKeyboardButton("🏠 Home", callback_data="back_main"))
    return mk

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
    markup.add(
        InlineKeyboardButton("⬅️ Back", callback_data="open_browse_services"),
        InlineKeyboardButton("🏠 Home", callback_data="back_main")
    )
    return markup

def get_recharge_menu():
    mk = InlineKeyboardMarkup(row_width=3)
    mk.row(
        InlineKeyboardButton("₹10", callback_data="setdep_10"),
        InlineKeyboardButton("₹50", callback_data="setdep_50"),
        InlineKeyboardButton("₹100", callback_data="setdep_100")
    )
    mk.row(
        InlineKeyboardButton("₹250", callback_data="setdep_250"),
        InlineKeyboardButton("₹500", callback_data="setdep_500"),
        InlineKeyboardButton("₹1000", callback_data="setdep_1000")
    )
    mk.add(InlineKeyboardButton("✏️ Custom Amount", callback_data="custom_dep_amt"))
    mk.add(
        InlineKeyboardButton("⬅️ Back", callback_data="back_main"),
        InlineKeyboardButton("🏠 Home", callback_data="back_main")
    )
    return mk

def send_zapupi_qr_card(chat_id, uid, amount):
    order_obj, qr_url, err = create_zapupi_order(uid, amount)
    if not order_obj:
        bot.send_message(chat_id, f"❌ <b>Payment Link generate nahi ho paya!</b>{err}\nSupport: {SUPPORT_USERNAME}", parse_mode="HTML")
        return

    caption = (
        f"<b>Tap 'Pay Now' button below to pay exact amount</b>\n\n"
        f"<b>Transaction ID:</b>\n"
        f"<code>{order_obj['order_id']}</code>\n\n"
        f"<blockquote>"
        f"❕ Note — Minimum deposit is ₹10\n"
        f"💯 Platform fee: {ZAPUPI_FEE_PERCENT:g}% (₹{order_obj['fee']:.2f})\n"
        f"💰 You receive: <b>₹{order_obj['net_credit']:.2f}</b> (after 2% fee)\n"
        f"🏷️ Payment note: <code>{order_obj['pay_note']}</code>"
        f"</blockquote>\n\n"
        f"Payment complete karne ke baad <b>Submit UTR / Txn ID</b> par tap karke apna <b>12-digit UTR number</b> bhejein.\n"
        f"<i>One UTR = One credit only.</i>"
    )
    mk = InlineKeyboardMarkup(row_width=1)
    mk.add(InlineKeyboardButton("💳 Pay Now (Instant UPI) ↗", url=order_obj["payment_url"]))
    mk.add(InlineKeyboardButton("⚙️ Submit UTR / Txn ID", callback_data=f"submit_utr_{order_obj['order_id']}"))
    mk.add(InlineKeyboardButton("🚫 Cancel Payment", callback_data=f"cancel_zap_{order_obj['order_id']}"))
    bot.send_photo(chat_id, photo=qr_url, caption=caption, reply_markup=mk, parse_mode="HTML")

def poll_otp_20_minutes(cid, uid, uname, activation_id, price, service_name, country_name, country_flag, phone):
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
                    user_recent_orders[uid] = {"service": service_name, "country": f"{country_flag} {country_name}", "phone": phone, "status": f"OTP Received ({otp})"}
                    bot.send_message(cid, f"✅ <b>Aapka OTP Code:</b> <code>{otp}</code>", parse_mode="HTML")
                    threading.Thread(target=send_sale_receipt, args=(service_name, country_name, country_flag, phone, activation_id, price, uid, uname)).start()
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
                            user_recent_orders[uid] = {"service": service_name, "country": f"{country_flag} {country_name}", "phone": phone, "status": f"OTP Received ({otp})"}
                            bot.send_message(cid, f"✅ <b>Aapka OTP Code:</b> <code>{otp}</code>", parse_mode="HTML")
                            threading.Thread(target=send_sale_receipt, args=(service_name, country_name, country_flag, phone, activation_id, price, uid, uname)).start()
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

@bot.message_handler(commands=["list", "users", "userlist"])
def admin_users_list(m):
    if m.from_user.id not in ALL_ADMINS:
        return
    conn = None
    rows = []
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, balance, COALESCE(purchased_count, 0), COALESCE(username, ''), COALESCE(nickname, '') FROM worldsim_users ORDER BY balance DESC, purchased_count DESC;")
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
        f"╭━━━✦ <b>WORLDSIM USER LIST</b> ✦━━━╮\n"
        f"👥 <b>Total Users:</b> {len(rows)}\n"
        f"💰 <b>Total Wallet Bal:</b> ₹{sum(float(r[1]) for r in rows):.2f}\n"
        f"🛒 <b>Total Accounts Bought:</b> {sum(int(r[2]) for r in rows)}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    chunk = header
    for idx, r in enumerate(rows, 1):
        uid_val, bal_val, buys_val, uname_val, nick_val = r
        display_user = f"{uname_val} ({nick_val}) [<code>{uid_val}</code>]" if uname_val else f"{nick_val or 'User'} [<code>{uid_val}</code>]"
        line = f"{idx}. {display_user} | Bal: <b>₹{float(bal_val):.2f}</b> | Buys: <b>{int(buys_val)}</b>\n"
        if len(chunk) + len(line) > 3800:
            bot.send_message(m.chat.id, chunk, parse_mode="HTML")
            chunk = ""
        chunk += line
    if chunk:
        bot.send_message(m.chat.id, chunk, parse_mode="HTML")

@bot.message_handler(commands=["cutuser"])
def admin_cut_by_username(m):
    if m.from_user.id not in ALL_ADMINS:
        return
    parts = m.text.split()
    if len(parts) < 3:
        bot.reply_to(m, "Format: <code>/cutuser @username <amount></code>", parse_mode="HTML")
        return
    uname_target = "@" + parts[1].replace("@", "")
    try:
        amount = float(parts[2])
    except ValueError:
        bot.reply_to(m, "Amount sahi number hona chahiye!")
        return
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id FROM worldsim_users WHERE LOWER(username) = LOWER(%s);", (uname_target,))
            r = cur.fetchone()
            if not r:
                bot.reply_to(m, f"❌ {uname_target} database me nahi mila!")
                return
            target_uid = int(r[0])
    finally:
        if conn:
            release_db_conn(conn)
    new_bal = update_bal(target_uid, -amount)
    bot.reply_to(m, f"✂️ Deducted ₹{amount:.2f} from {uname_target} (<code>{target_uid}</code>)\nRemaining Balance: <b>₹{new_bal:.2f}</b>", parse_mode="HTML")

@bot.message_handler(commands=["broadcast", "sendall", "update"])
def broadcast_message(m):
    if m.from_user.id not in ALL_ADMINS:
        return
    msg_text = m.text.split(" ", 1)[1].strip() if " " in m.text else "🚀 WorldSIM Hub ab fir se open ho gaya hai! Ab aap instant OTP aur virtual numbers buy kar sakte hain."
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
            bot.send_message(user[0], f"📢 <b>WorldSIM Hub Notice:</b>\n\n{msg_text}", parse_mode="HTML")
            sent += 1
            time.sleep(0.05)
        except Exception:
            pass
    bot.send_message(m.chat.id, f"✅ Broadcast Complete! Delivered: <b>{sent}</b>", parse_mode="HTML")

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
    bot.reply_to(m, f"👤 <b>User Details:</b>\n\n• <b>User ID:</b> <code>{target_uid}</code>\n• <b>Balance:</b> <b>₹{user_bal:.2f}</b>\n• <b>Accounts Bought:</b> <b>{buys}</b>\n• <b>Referred By:</b> <code>{ref_by if ref_by != 0 else 'None'}</code>", parse_mode="HTML")

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

@bot.message_handler(commands=["start"])
def start(m):
    uid = m.from_user.id
    name = m.from_user.first_name or "User"
    sync_user_info(uid, m.from_user.username, name)
    parts = m.text.split()
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            set_referrer(uid, int(parts[1].replace("ref_", "")))
        except Exception:
            pass
    if not is_user_member(uid):
        send_force_join_prompt(m.chat.id)
        return
    bal, _, _ = get_user(uid)
    process_referral_reward(uid)
    if len(parts) > 1 and parts[1] == "buy":
        bot.send_message(m.chat.id, "<blockquote>🛒 <b>Select Service</b>\nChoose your preferred OTP service below:</blockquote>", reply_markup=get_service_picker_menu(), parse_mode="HTML")
        return
    bot.send_message(m.chat.id, build_home_text(name, uid, bal), reply_markup=get_home_menu(), parse_mode="HTML")

@bot.message_handler(func=lambda m: not m.text.startswith("/"))
def text_flow(m):
    uid = m.from_user.id
    name = m.from_user.first_name or "User"
    sync_user_info(uid, m.from_user.username, name)
    if not is_user_member(uid):
        send_force_join_prompt(m.chat.id)
        return

    raw = m.text.strip()
    state = user_input_state.get(uid)

    if state == "awaiting_custom_amount":
        user_input_state.pop(uid, None)
        if not raw.replace(".", "", 1).isdigit():
            bot.reply_to(m, "⚠️ Kripya sahi amount enter karein (Minimum ₹10).")
            return
        amt = float(raw)
        if amt < 10:
            bot.reply_to(m, "⚠️ Minimum deposit ₹10 hai!")
            return
        send_zapupi_qr_card(m.chat.id, uid, amt)
        return

    if state and state.startswith("awaiting_utr_"):
        order_id = state.replace("awaiting_utr_", "")
        utr = raw.strip()
        if not re.fullmatch(r"\d{12}", utr):
            bot.reply_to(m, "⚠️ <b>Sirf 12-digit numeric UTR number enter karein!</b>\n<i>(PhonePe ka 'T2611...' Transaction ID nahi, neeche likha 12-digit UTR number dalein)</i>", parse_mode="HTML")
            return

        if is_utr_or_order_used(utr, order_id):
            user_input_state.pop(uid, None)
            bot.reply_to(m, "❌ <b>Yeh UTR ya Order pehle hi verify ho chuka hai!</b>\n<i>One UTR = One credit only.</i>", parse_mode="HTML")
            return

        order_obj = pending_zap_orders.get(uid)
        if not order_obj or order_obj["order_id"] != order_id:
            user_input_state.pop(uid, None)
            bot.reply_to(m, "⚠️ Order expire ho gaya hai. Kripya dubara Recharge par click karein.")
            return

        wait_m = bot.reply_to(m, "⏳ <b>Payment UTR verify kiya ja raha hai...</b>", parse_mode="HTML")
        ok, msg_status = verify_zapupi_utr(order_id, utr)
        if ok:
            if not mark_utr_and_order_used(utr, order_id, uid, order_obj["net_credit"]):
                bot.edit_message_text("❌ <b>Yeh UTR pehle hi use ho chuka hai!</b>", chat_id=m.chat.id, message_id=wait_m.message_id, parse_mode="HTML")
                return
            user_input_state.pop(uid, None)
            pending_zap_orders.pop(uid, None)
            new_bal = update_bal(uid, order_obj["net_credit"])
            bot.edit_message_text(
                f"✅ <b>Deposit Verified!</b>\n\n"
                f"• <b>Paid:</b> ₹{order_obj['amount']:.2f}\n"
                f"• <b>Platform Fee (2%):</b> -₹{order_obj['fee']:.2f}\n"
                f"• <b>Credited:</b> <b>+₹{order_obj['net_credit']:.2f}</b>\n"
                f"• <b>New Wallet Balance:</b> <b>₹{new_bal:.2f}</b>",
                chat_id=m.chat.id, message_id=wait_m.message_id, parse_mode="HTML"
            )
            for adm in ALL_ADMINS:
                try:
                    bot.send_message(adm, f"💰 <b>WorldSIM Hub — Instant UPI Deposit!</b>\nUser: <code>{uid}</code>\nPaid: ₹{order_obj['amount']:.2f} | Added: ₹{order_obj['net_credit']:.2f}\nUTR: <code>{utr}</code>", parse_mode="HTML")
                except Exception:
                    pass
        else:
            bot.edit_message_text(
                f"❌ <b>Verification Failed:</b> {msg_status}\n\n"
                f"Agar aapne abhi payment kiya hai toh 10 second ruk kar dobara 12-digit UTR bhejein ya support se contact karein: {SUPPORT_USERNAME}",
                chat_id=m.chat.id, message_id=wait_m.message_id, parse_mode="HTML"
            )
        return

    if uid in user_search_state:
        service = user_search_state.pop(uid)
        matches = [c for c in get_service_catalog(service) if raw.lower() in c["name"].lower()]
        if not matches:
            bot.reply_to(m, f"❌ '<b>{raw}</b>' naam ka koi country nahi mila!", reply_markup=get_home_menu(), parse_mode="HTML")
            return
        mk = InlineKeyboardMarkup(row_width=2)
        btns = [InlineKeyboardButton(f"{c['flag']} {c['name']} • ₹{c['price']:g}", callback_data=f"buy_{service}_{c['id']}_{c['price']}") for c in matches]
        for i in range(0, len(btns), 2):
            mk.row(*btns[i:i+2])
        mk.add(InlineKeyboardButton("⬅️ Back", callback_data="open_browse_services"))
        bot.reply_to(m, f"🔍 <b>Search Results for '{raw}':</b>", reply_markup=mk, parse_mode="HTML")
        return

    if raw.replace(".", "", 1).isdigit():
        amt = float(raw)
        if amt >= 10:
            send_zapupi_qr_card(m.chat.id, uid, amt)
            return

    bot.reply_to(m, "👇 Neeche diye gaye menu buttons ka use karein:", reply_markup=get_home_menu())

@bot.callback_query_handler(func=lambda call: True)
def callbacks(call):
    uid = call.from_user.id
    uname = call.from_user.username
    name = call.from_user.first_name or "User"
    sync_user_info(uid, uname, name)

    if call.data == "check_join":
        unjoined = get_user_unjoined_channels(uid)
        if not unjoined:
            bal, _, _ = get_user(uid)
            process_referral_reward(uid)
            bot.edit_message_text(build_home_text(name, uid, bal), chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_home_menu(), parse_mode="HTML")
        else:
            bot.answer_callback_query(call.id, f"⚠️ Abhi {len(unjoined)} channel(s) baaki hain!", show_alert=True)
        return

    if not is_user_member(uid) and uid not in ALL_ADMINS:
        bot.answer_callback_query(call.id, "⚠️ Pehle dono channels join karein!", show_alert=True)
        return

    bal, _, buys = get_user(uid)

    if call.data == "ignore":
        bot.answer_callback_query(call.id)
    elif call.data == "back_main":
        user_input_state.pop(uid, None)
        text = build_home_text(name, uid, bal)
        if call.message.photo:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text, reply_markup=get_home_menu(), parse_mode="HTML")
        else:
            bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_home_menu(), parse_mode="HTML")
    elif call.data == "open_browse_services":
        text = "<blockquote>🛒 <b>Select OTP Service</b>\nChoose a platform below to view available countries:</blockquote>"
        if call.message.photo:
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, text, reply_markup=get_service_picker_menu(), parse_mode="HTML")
        else:
            bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_service_picker_menu(), parse_mode="HTML")
    elif call.data.startswith("page_"):
        parts = call.data.split("_")
        service, page = parts[1], int(parts[2])
        s_name = SERVICES.get(service, {}).get("name", "Service")
        text = f"<blockquote>🌐 <b>{s_name} Servers</b>\nSelect country to buy instant OTP account:</blockquote>"
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_countries_paged_menu(service, page), parse_mode="HTML")
    elif call.data.startswith("search_country_"):
        user_search_state[uid] = call.data.replace("search_country_", "")
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🔍 <b>Country ka naam type karein:</b>", parse_mode="HTML")
    elif call.data == "menu_dep":
        text = (
            "✦━━━━━━━━━━━━━━━✦\n"
            "🇮🇳 <b>PAY VIA UPI</b>\n"
            "✦━━━━━━━━━━━━━━━✦\n\n"
            f"💲 <b>Balance:</b> ₹{bal:.2f}\n\n"
            "<blockquote>"
            "📌 Pay via Instant UPI · auto verify via UTR\n"
            f"💯 Platform fee · {ZAPUPI_FEE_PERCENT:g}%\n"
            "⚡ One UTR = one credit only"
            "</blockquote>\n\n"
            "👇 <i>Select amount:</i>"
        )
        bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=get_recharge_menu(), parse_mode="HTML")
    elif call.data == "custom_dep_amt":
        user_input_state[uid] = "awaiting_custom_amount"
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "✏️ <b>Enter custom deposit amount in ₹ (Minimum ₹10):</b>", parse_mode="HTML")
    elif call.data.startswith("setdep_"):
        amt = float(call.data.split("_")[1])
        bot.answer_callback_query(call.id, "Creating Instant UPI Order...")
        send_zapupi_qr_card(call.message.chat.id, uid, amt)
    elif call.data.startswith("submit_utr_"):
        order_id = call.data.replace("submit_utr_", "")
        user_input_state[uid] = f"awaiting_utr_{order_id}"
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔢 <b>Send your exact 12-digit UTR Number for</b> <code>{order_id}</code>:", parse_mode="HTML")
    elif call.data.startswith("cancel_zap_"):
        pending_zap_orders.pop(uid, None)
        user_input_state.pop(uid, None)
        bot.answer_callback_query(call.id, "Payment Cancelled")
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, build_home_text(name, uid, bal), reply_markup=get_home_menu(), parse_mode="HTML")
    elif call.data == "menu_terms":
        terms_text = (
            "<blockquote>"
            "📋 <b>Terms of Service</b>\n"
            "<i>By using this bot you agree to all terms below.</i>\n\n"
            "<b>1. No Refunds</b>\n"
            "All sales are final. No refunds under any circumstances.\n\n"
            "<b>2. Sub-₹40 Rule</b>\n"
            "Accounts priced below ₹40 carry no warranty for login failures or missing codes.\n\n"
            "<b>3. No Re-logins</b>\n"
            "Sessions are permanently closed after purchase. One login only.\n\n"
            "<b>4. Premium Accounts</b>\n"
            "Cheap quality accounts may last only 1–2 days. Buy at your own risk. No refunds.\n\n"
            "<b>5. No Longevity Guarantee</b>\n"
            "We do not guarantee account lifespan, 2FA status or spam block status.\n\n"
            "<b>6. Liability</b>\n"
            "Use at your own risk. We are not responsible for loss of funds or accounts.\n\n"
            "<i>Developed by - kissu (achi bachi)</i>"
            "</blockquote>"
        )
        mk = InlineKeyboardMarkup(row_width=1)
        mk.add(InlineKeyboardButton("🛒 Browse Accounts", callback_data="open_browse_services"))
        mk.add(InlineKeyboardButton("🏠 Home", callback_data="back_main"))
        bot.edit_message_text(terms_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=mk, parse_mode="HTML")
    elif call.data in ["menu_profile", "menu_refer"]:
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
            "<blockquote>"
            f"👤 <b>Profile & Referrals</b>\n\n"
            f"🪪 <b>ID:</b> <code>{uid}</code>\n"
            f"💲 <b>Wallet:</b> ₹{bal:.2f}\n"
            f"📦 <b>Accounts Bought:</b> {buys}\n"
            f"👥 <b>Total Referrals:</b> {refs}\n"
            f"🎁 <b>Earned:</b> ₹{round(refs * PER_REFER_REWARD, 2):.2f} (₹{PER_REFER_REWARD:.2f}/refer)\n\n"
            f"🔗 <b>Referral Link:</b>\n<code>{ref_link}</code>"
            "</blockquote>"
        )
        mk = InlineKeyboardMarkup(row_width=2)
        mk.add(
            InlineKeyboardButton("💲 Recharge", callback_data="menu_dep"),
            InlineKeyboardButton("🏠 Home", callback_data="back_main")
        )
        bot.edit_message_text(prof_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=mk, parse_mode="HTML")
    elif call.data == "menu_orders":
        last_ord = user_recent_orders.get(uid)
        ord_text = "<blockquote>📦 <b>Aapka koi recent order nahi hai.</b></blockquote>" if not last_ord else f"<blockquote>📑 <b>Recent Order</b>\n\n• <b>Service:</b> {last_ord.get('service')}\n• <b>Country:</b> {last_ord.get('country')}\n• <b>Number:</b> <code>+{last_ord.get('phone')}</code>\n• <b>Status:</b> {last_ord.get('status')}</blockquote>"
        mk = InlineKeyboardMarkup(row_width=2)
        mk.add(
            InlineKeyboardButton("🛒 Buy Account", callback_data="open_browse_services"),
            InlineKeyboardButton("🏠 Home", callback_data="back_main")
        )
        bot.edit_message_text(ord_text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=mk, parse_mode="HTML")
    elif call.data.startswith("rate_"):
        parts = call.data.split("_")
        stars = int(parts[1])
        s_name = parts[2] if len(parts) > 2 else "OTP Service"
        bot.answer_callback_query(call.id, f"Aapne {stars} Star diya!")
        bot.edit_message_text(f"💖 <b>Feedback ke liye shukriya!</b> ({'⭐' * stars})", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="HTML")
        threading.Thread(target=send_feedback_receipt_to_channel, args=(uid, stars, s_name, uname)).start()
    elif call.data.startswith("cancel_order_"):
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
    elif call.data.startswith("buy_"):
        parts = call.data.split("_")
        service, code, p = parts[1], parts[2], float(parts[3])
        s_name = SERVICES.get(service, {}).get("name", service.upper())
        country_data = next((c for c in get_service_catalog(service) if c["id"] == code), {"name": "Country", "flag": "🌐"})
        if get_bal(uid) < p:
            bot.answer_callback_query(call.id, f"Balance kam hai! Price: ₹{p}, Bal: ₹{get_bal(uid):.2f}", show_alert=True)
            return
        bot.answer_callback_query(call.id, f"Ordering {s_name}...")
        wait_msg = bot.send_message(call.message.chat.id, f"🔄 {country_data.get('flag')} {country_data.get('name')} {s_name} number manga rahe hain...")
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
            "<blockquote>"
            f"📱 <b>Number:</b> <code>+{phone}</code>\n"
            f"🌍 <b>Country:</b> {country_data.get('flag')} {country_data.get('name')}\n"
            f"💸 <b>Deducted:</b> ₹{p:.2f}\n"
            f"⏳ <b>Waiting for OTP... (20 Min)</b>"
            "</blockquote>"
        )
        bot.send_message(call.message.chat.id, order_text, reply_markup=cancel_mk, parse_mode="HTML")
        threading.Thread(target=poll_otp_20_minutes, args=(call.message.chat.id, uid, uname, activation_id, p, s_name, country_data.get("name"), country_data.get("flag"), phone)).start()

print(">> WORLDSIM HUB BOT RUNNING LIVE <<")
while True:
    try:
        bot.polling(none_stop=True, timeout=30, long_polling_timeout=30)
    except Exception as e:
        print(f"Connection retry error: {e}")
        time.sleep(3)
