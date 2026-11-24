import os
import re
import uuid
import time
import hashlib
import datetime
import threading
import urllib.parse
import requests
import psycopg2
from psycopg2 import pool
from flask import Flask, request, jsonify, session, render_template_string

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "worldsim_hub_vip_super_secret_key_2026")

# ================= CONFIGURATION =================
BOT_TOKEN = "9109714291:AAFQny4eo62NZQy7TAnxXJQf3dG420gw2O4"
SASTA_API_KEY = "stp_4905928f4de82481bad70ffd7d8da6b59e82e625396bebc3"
BASE_URL = "https://sastasms.pro/stubs/handler_api.php"

ZAPUPI_API_KEY = "zap81dd07798ad86781b13f7e7e632d1486"
ZAPUPI_FEE_PERCENT = 2.0
MERCHANT_UPI_ID = "paytm.s4qvafn@pty"
MERCHANT_NAME = "WorldSIM Hub"

DATABASE_URL = "postgresql://neondb_owner:npg_Hy4LqEYdOvk7@ep-weathered-river-bdjtcb91-pooler.c-8.us-east-2.aws.neon.tech/neondb?sslmode=require"

ADMIN_EMAILS = ["ub22q@gmail.com", "worldsimhub@gmail.com"]
ADMIN_UIDS = [8539777823, 9013970075]

SUPPORT_USERNAME = "@Worldsim_hub"
SUPPORT_LINK = "https://t.me/Worldsim_hub"
RECEIPT_CHANNEL_ID = -1004497033717

PER_REFER_REWARD = 0.70
TELEGRAM_MARGIN_INR = 10.0

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

tg_live_price_cache = {"time": 0, "prices": {}}
pending_zap_orders = {}
active_app_orders = {}
# --- END OF PART 1 ---
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

def hash_pw(pw):
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

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
                nickname TEXT DEFAULT '',
                email TEXT DEFAULT '',
                password_hash TEXT DEFAULT ''
            );
            """)
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS email TEXT DEFAULT '';")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS password_hash TEXT DEFAULT '';")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS purchased_count INT DEFAULT 0;")
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
        print(f"DB Init Error: {e}")
    finally:
        if conn:
            release_db_conn(conn)

init_db()

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

def get_full_catalog():
    live_tg = get_telegram_live_catalog()
    out = {}
    for srv, items in CATALOG.items():
        srv_list = []
        for c in items:
            item = dict(c)
            if srv == "tg" and item["id"] in live_tg:
                item["price"] = live_tg[item["id"]]
            srv_list.append(item)
        out[srv] = srv_list
    return out

def update_bal(uid, amt):
    uid = int(uid)
    amt = float(amt)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("""
            UPDATE worldsim_users
            SET balance = GREATEST(0.0, balance + %s)
            WHERE user_id = %s
            RETURNING balance;
            """, (amt, uid))
            row = cur.fetchone()
            new_bal = float(row[0]) if row else 0.0
        conn.commit()
        return round(new_bal, 2)
    except Exception as e:
        print(f"update_bal error: {e}")
        return 0.0
    finally:
        if conn:
            release_db_conn(conn)

def send_sale_receipt_tg(service_name, country_name, country_flag, phone_num, activation_id, price_inr, buyer_label):
    str_phone = str(phone_num)
    masked_phone = str_phone[:4] + "••••" + str_phone[-2:] if len(str_phone) > 6 else str_phone[:2] + "••••"
    now_str = datetime.datetime.now().strftime("%d %b %Y  %H:%M")
    price_usd = round(price_inr / 88.0, 2)
    receipt = (
        "+--------------------------------------+\n"
        "|   WORLDSIM HUB APP • SALE RECEIPT    |\n"
        "+--------------------------------------+\n"
        "|                                      |\n"
        f"|  Status     : OTP DELIVERED OK       |\n"
        f"|  Buyer      : {buyer_label[:23]:<23}|\n"
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
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={"chat_id": RECEIPT_CHANNEL_ID, "text": f"```\n{receipt}\n```", "parse_mode": "Markdown"},
            timeout=5
        )
    except Exception:
        pass
# --- END OF PART 2 ---
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    if not email or not password:
        return jsonify({"ok": False, "error": "Gmail aur Password dono dalein!"})

    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, balance, COALESCE(purchased_count, 0), COALESCE(nickname, 'User'), password_hash FROM worldsim_users WHERE LOWER(email) = %s;", (email,))
            r = cur.fetchone()
            if not r:
                return jsonify({"ok": False, "error": "Is Gmail se koi account nahi mila. Pehle Sign Up karein!"})
            if r[4] != hash_pw(password):
                return jsonify({"ok": False, "error": "Password galat hai!"})
            uid = int(r[0])
            session["uid"] = uid
            session["email"] = email
            is_admin = (email in ADMIN_EMAILS) or (uid in ADMIN_UIDS)
            return jsonify({
                "ok": True,
                "user": {
                    "uid": uid,
                    "email": email,
                    "name": r[3] or email.split("@")[0],
                    "balance": round(float(r[1]), 2),
                    "buys": int(r[2]),
                    "is_admin": is_admin
                }
            })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
    finally:
        if conn:
            release_db_conn(conn)

@app.route("/api/auth/signup", methods=["POST"])
def api_signup():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = (data.get("password") or "").strip()
    name = (data.get("name") or "").strip() or email.split("@")[0]
    tg_id_raw = str(data.get("tg_id") or "").strip()

    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
        return jsonify({"ok": False, "error": "Valid Gmail address enter karein!"})
    if len(password) < 4:
        return jsonify({"ok": False, "error": "Password kam se kam 4 characters ka rakhein!"})

    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM worldsim_users WHERE LOWER(email) = %s;", (email,))
            if cur.fetchone():
                return jsonify({"ok": False, "error": "Yeh Gmail pehle se registered hai! Login karein."})

            if tg_id_raw.isdigit():
                uid = int(tg_id_raw)
                cur.execute("SELECT balance, COALESCE(purchased_count, 0), COALESCE(email, '') FROM worldsim_users WHERE user_id = %s;", (uid,))
                existing = cur.fetchone()
                if existing:
                    if existing[2]:
                        return jsonify({"ok": False, "error": "Is Telegram ID par pehle se ek Gmail linked hai!"})
                    cur.execute("UPDATE worldsim_users SET email = %s, password_hash = %s, nickname = %s WHERE user_id = %s;", (email, hash_pw(password), name, uid))
                    bal, buys = float(existing[0]), int(existing[1])
                else:
                    cur.execute("INSERT INTO worldsim_users (user_id, balance, referred_by, purchased_count, ref_paid, pending_dep, username, nickname, email, password_hash) VALUES (%s, 0.0, 0, 0, FALSE, FALSE, '', %s, %s, %s);", (uid, name, email, hash_pw(password)))
                    bal, buys = 0.0, 0
            else:
                uid = int(str(int(time.time()))[-6:] + str(uuid.uuid4().int)[:4])
                cur.execute("INSERT INTO worldsim_users (user_id, balance, referred_by, purchased_count, ref_paid, pending_dep, username, nickname, email, password_hash) VALUES (%s, 0.0, 0, 0, FALSE, FALSE, '', %s, %s, %s);", (uid, name, email, hash_pw(password)))
                bal, buys = 0.0, 0

        conn.commit()
        session["uid"] = uid
        session["email"] = email
        is_admin = (email in ADMIN_EMAILS) or (uid in ADMIN_UIDS)
        return jsonify({
            "ok": True,
            "user": {
                "uid": uid,
                "email": email,
                "name": name,
                "balance": round(bal, 2),
                "buys": buys,
                "is_admin": is_admin
            }
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})
    finally:
        if conn:
            release_db_conn(conn)

@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})

@app.route("/api/me")
def api_me():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False})
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT balance, COALESCE(purchased_count, 0), COALESCE(nickname, 'User'), COALESCE(email, '') FROM worldsim_users WHERE user_id = %s;", (uid,))
            r = cur.fetchone()
            if not r:
                session.clear()
                return jsonify({"ok": False})
            email = r[3]
            is_admin = (email in ADMIN_EMAILS) or (int(uid) in ADMIN_UIDS)
            return jsonify({
                "ok": True,
                "user": {
                    "uid": int(uid),
                    "email": email,
                    "name": r[2],
                    "balance": round(float(r[0]), 2),
                    "buys": int(r[1]),
                    "is_admin": is_admin
                },
                "catalog": get_full_catalog(),
                "orders": active_app_orders.get(int(uid), [])
            })
    except Exception:
        return jsonify({"ok": False})
    finally:
        if conn:
            release_db_conn(conn)
# --- END OF PART 3 ---
@app.route("/api/deposit/create", methods=["POST"])
def api_deposit_create():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False, "error": "Please login first"})
    data = request.json or {}
    try:
        amount = float(data.get("amount", 0))
    except ValueError:
        return jsonify({"ok": False, "error": "Invalid amount"})
    if amount < 10:
        return jsonify({"ok": False, "error": "Minimum deposit ₹10 hai!"})

    order_id = f"{int(time.time())}{str(uid)[-4:]}"
    fee = round(amount * (ZAPUPI_FEE_PERCENT / 100.0), 2)
    net_credit = round(amount - fee, 2)
    pay_note = f"WorldSIM{order_id[-6:]}"

    payment_url = None
    upi_intent_str = None
    err_msg = ""
    try:
        payload = {
            "zap_key": ZAPUPI_API_KEY,
            "order_id": order_id,
            "amount": str(int(amount) if amount.is_integer() else amount),
            "customer_mobile": "9876543210",
            "remark": pay_note
        }
        resp = requests.post("https://pay.zapupi.com/api/create-order", json=payload, headers={"Content-Type": "application/json"}, timeout=10)
        res_data = resp.json()
        if str(res_data.get("status", "")).lower() == "success":
            payment_url = res_data.get("payment_url")
            upi_intent_str = res_data.get("upi_intent") or res_data.get("upi_link") or payment_url
        else:
            err_msg = res_data.get("message", "Payment link creation failed")
    except Exception as e:
        err_msg = str(e)

    if not payment_url:
        return jsonify({"ok": False, "error": f"Gateway error: {err_msg}"})

    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=300x300&data={urllib.parse.quote(upi_intent_str)}"
    order_obj = {
        "order_id": order_id,
        "amount": amount,
        "fee": fee,
        "net_credit": net_credit,
        "pay_note": pay_note,
        "payment_url": payment_url,
        "qr_url": qr_url
    }
    pending_zap_orders[int(uid)] = order_obj
    return jsonify({"ok": True, "order": order_obj})

@app.route("/api/deposit/verify", methods=["POST"])
def api_deposit_verify():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False, "error": "Please login first"})
    uid = int(uid)
    data = request.json or {}
    order_id = str(data.get("order_id") or "").strip()
    utr = str(data.get("utr") or "").strip()

    if not re.fullmatch(r"\d{12}", utr):
        return jsonify({"ok": False, "error": "Sirf 12-digit numeric UTR number enter karein!"})

    order_obj = pending_zap_orders.get(uid)
    if not order_obj or order_obj["order_id"] != order_id:
        return jsonify({"ok": False, "error": "Order expire ho gaya hai. Dubara amount select karein!"})

    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM used_utrs WHERE utr = %s;", (utr,))
            if cur.fetchone():
                return jsonify({"ok": False, "error": "Yeh UTR pehle hi use ho chuka hai!"})
            cur.execute("SELECT 1 FROM verified_orders WHERE order_id = %s;", (order_id,))
            if cur.fetchone():
                return jsonify({"ok": False, "error": "Yeh Order pehle hi verify ho chuka hai!"})
    finally:
        if conn:
            release_db_conn(conn)

    try:
        r = requests.post("https://pay.zapupi.com/api/order-status", json={"zap_key": ZAPUPI_API_KEY, "order_id": order_id}, headers={"Content-Type": "application/json"}, timeout=10)
        res = r.json()
        st = str(res.get("status", "")).lower()
        d_obj = res.get("data") if isinstance(res.get("data"), dict) else {}
        t_st = str(d_obj.get("status", "")).lower()
        if st in ["success", "paid", "completed"] or t_st in ["success", "paid", "completed"]:
            api_utr = str(res.get("utr") or d_obj.get("utr") or "").strip()
            if api_utr and api_utr != utr:
                return jsonify({"ok": False, "error": "UTR is order se match nahi hua!"})
        else:
            return jsonify({"ok": False, "error": res.get("message", "Abhi payment complete nahi dikh raha!")})
    except Exception:
        return jsonify({"ok": False, "error": "Payment server connection error"})

    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("INSERT INTO used_utrs (utr, user_id, amount) VALUES (%s, %s, %s);", (utr, uid, order_obj["net_credit"]))
            cur.execute("INSERT INTO verified_orders (order_id, user_id, utr, amount) VALUES (%s, %s, %s, %s);", (order_id, uid, utr, order_obj["net_credit"]))
        conn.commit()
    except Exception:
        return jsonify({"ok": False, "error": "UTR already used!"})
    finally:
        if conn:
            release_db_conn(conn)

    pending_zap_orders.pop(uid, None)
    new_bal = update_bal(uid, order_obj["net_credit"])
    for adm in ADMIN_UIDS:
        try:
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={"chat_id": adm, "text": f"💰 <b>WorldSIM Hub App — Instant UPI Deposit!</b>\nUser ID: <code>{uid}</code>\nPaid: ₹{order_obj['amount']:.2f} | Added: ₹{order_obj['net_credit']:.2f}\nUTR: <code>{utr}</code>", "parse_mode": "HTML"},
                timeout=5
            )
        except Exception:
            pass
    return jsonify({"ok": True, "new_balance": new_bal, "credited": order_obj["net_credit"]})

@app.route("/api/otp/buy", methods=["POST"])
def api_otp_buy():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False, "error": "Please login first"})
    uid = int(uid)
    data = request.json or {}
    service = str(data.get("service") or "")
    country_id = str(data.get("country_id") or "")

    catalog = get_full_catalog().get(service, [])
    country_item = next((c for c in catalog if c["id"] == country_id), None)
    if not country_item:
        return jsonify({"ok": False, "error": "Invalid service or country"})

    price = float(country_item["price"])
    conn = None
    bal = 0.0
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM worldsim_users WHERE user_id = %s;", (uid,))
            r = cur.fetchone()
            bal = float(r[0]) if r else 0.0
    finally:
        if conn:
            release_db_conn(conn)

    if bal < price:
        return jsonify({"ok": False, "error": f"Balance kam hai! Price: ₹{price:.2f}, Balance: ₹{bal:.2f}"})

    try:
        res = requests.get(f"{BASE_URL}?api_key={SASTA_API_KEY}&action=getNumber&service={service}&country={country_id}&format=json", timeout=10).json()
    except Exception:
        return jsonify({"ok": False, "error": "Server connection error!"})

    act_id = str(res.get("activation_id") or res.get("id") or "")
    phone = str(res.get("phone") or res.get("number") or "")
    if not phone or not act_id:
        return jsonify({"ok": False, "error": res.get("error") or res.get("msg") or "Stock unavailable"})

    new_bal = update_bal(uid, -price)
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("UPDATE worldsim_users SET purchased_count = COALESCE(purchased_count, 0) + 1 WHERE user_id = %s;", (uid,))
        conn.commit()
    finally:
        if conn:
            release_db_conn(conn)

    order_record = {
        "activation_id": act_id,
        "service": SERVICES.get(service, {}).get("name", service.upper()),
        "country": f"{country_item['flag']} {country_item['name']}",
        "country_name": country_item["name"],
        "country_flag": country_item["flag"],
        "phone": phone,
        "price": price,
        "status": "waiting",
        "otp": "",
        "created_at": time.time()
    }
    active_app_orders.setdefault(uid, []).insert(0, order_record)
    return jsonify({"ok": True, "order": order_record, "new_balance": new_bal})

@app.route("/api/otp/status/<act_id>")
def api_otp_status(act_id):
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False})
    uid = int(uid)
    orders = active_app_orders.get(uid, [])
    ord_obj = next((o for o in orders if o["activation_id"] == act_id), None)
    if not ord_obj:
        return jsonify({"ok": False, "error": "Order not found"})

    if ord_obj["status"] in ["received", "cancelled"]:
        return jsonify({"ok": True, "order": ord_obj})

    if time.time() - ord_obj["created_at"] > 1200:
        try:
            requests.get(f"{BASE_URL}?api_key={SASTA_API_KEY}&action=setStatus&status=8&id={act_id}", timeout=5)
        except Exception:
            pass
        ord_obj["status"] = "cancelled"
        new_bal = update_bal(uid, ord_obj["price"])
        return jsonify({"ok": True, "order": ord_obj, "new_balance": new_bal, "refunded": True})

    try:
        r = requests.get(f"{BASE_URL}?api_key={SASTA_API_KEY}&action=getStatus&id={act_id}", timeout=5)
        txt = r.text.strip()
        otp = None
        if "STATUS_OK" in txt:
            parts = txt.split(":")
            otp = parts[1] if len(parts) > 1 else txt
        elif "STATUS_CANCEL" in txt:
            ord_obj["status"] = "cancelled"
            new_bal = update_bal(uid, ord_obj["price"])
            return jsonify({"ok": True, "order": ord_obj, "new_balance": new_bal, "refunded": True})
        else:
            try:
                j = r.json()
                if j.get("status") == "STATUS_OK" or "code" in j:
                    otp = j.get("code") or j.get("sms")
            except Exception:
                pass

        if otp and str(otp).lower() != "none":
            ord_obj["status"] = "received"
            ord_obj["otp"] = str(otp)
            buyer_label = session.get("email", f"ID:{uid}")
            threading.Thread(target=send_sale_receipt_tg, args=(ord_obj["service"], ord_obj["country_name"], ord_obj["country_flag"], ord_obj["phone"], act_id, ord_obj["price"], buyer_label)).start()
    except Exception:
        pass

    return jsonify({"ok": True, "order": ord_obj})

@app.route("/api/otp/cancel/<act_id>", methods=["POST"])
def api_otp_cancel(act_id):
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False})
    uid = int(uid)
    orders = active_app_orders.get(uid, [])
    ord_obj = next((o for o in orders if o["activation_id"] == act_id), None)
    if not ord_obj or ord_obj["status"] != "waiting":
        return jsonify({"ok": False, "error": "Cannot cancel this order"})

    try:
        requests.get(f"{BASE_URL}?api_key={SASTA_API_KEY}&action=setStatus&status=8&id={act_id}", timeout=5)
    except Exception:
        pass
    ord_obj["status"] = "cancelled"
    new_bal = update_bal(uid, ord_obj["price"])
    return jsonify({"ok": True, "new_balance": new_bal})

@app.route("/api/admin/users")
def api_admin_users():
    uid = session.get("uid")
    email = session.get("email", "")
    if not uid or (email not in ADMIN_EMAILS and int(uid) not in ADMIN_UIDS):
        return jsonify({"ok": False, "error": "Unauthorized"})
    conn = None
    try:
        conn = get_db_conn()
        with conn.cursor() as cur:
            cur.execute("SELECT user_id, balance, COALESCE(purchased_count, 0), COALESCE(username, ''), COALESCE(nickname, ''), COALESCE(email, '') FROM worldsim_users ORDER BY balance DESC, purchased_count DESC;")
            rows = cur.fetchall()
            users = [{"uid": int(r[0]), "balance": round(float(r[1]), 2), "buys": int(r[2]), "username": r[3], "nickname": r[4], "email": r[5]} for r in rows]
            return jsonify({"ok": True, "users": users})
    finally:
        if conn:
            release_db_conn(conn)

@app.route("/api/admin/balance", methods=["POST"])
def api_admin_balance():
    uid = session.get("uid")
    email = session.get("email", "")
    if not uid or (email not in ADMIN_EMAILS and int(uid) not in ADMIN_UIDS):
        return jsonify({"ok": False, "error": "Unauthorized"})
    data = request.json or {}
    target_uid = int(data.get("target_uid", 0))
    delta = float(data.get("delta", 0))
    new_bal = update_bal(target_uid, delta)
    return jsonify({"ok": True, "new_balance": new_bal})
# --- END OF PART 4 ---
APP_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<meta name="theme-color" content="#090d16">
<title>WorldSIM Hub — Instant Virtual OTP</title>
<style>
  :root {
    --bg: #090d16; --card: #121826; --card2: #192236; --border: rgba(255,255,255,0.08);
    --primary: #3b82f6; --accent: #10b981; --danger: #ef4444; --text: #f8fafc; --muted: #94a3b8;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; -webkit-tap-highlight-color: transparent; }
  body { background: var(--bg); color: var(--text); max-width: 480px; margin: 0 auto; min-height: 100vh; padding-bottom: 84px; }
  .header { position: sticky; top: 0; z-index: 50; background: rgba(9,13,22,0.9); backdrop-filter: blur(12px); padding: 14px 18px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }
  .brand { font-size: 18px; font-weight: 800; letter-spacing: 0.3px; display: flex; align-items: center; gap: 8px; }
  .brand span { color: var(--primary); }
  .bal-pill { background: linear-gradient(135deg, rgba(16,185,129,0.18), rgba(59,130,246,0.18)); border: 1px solid rgba(16,185,129,0.4); padding: 6px 12px; border-radius: 99px; font-size: 13px; font-weight: 700; color: #34d399; }
  .container { padding: 16px; }
  .card { background: var(--card); border: 1px solid var(--border); border-radius: 18px; padding: 16px; margin-bottom: 14px; }
  .hero-card { background: linear-gradient(135deg, #16223b 0%, #0f172a 100%); border: 1px solid rgba(59,130,246,0.3); border-radius: 20px; padding: 20px; margin-bottom: 16px; position: relative; overflow: hidden; }
  .hero-bal { font-size: 32px; font-weight: 800; margin: 6px 0 12px; color: #fff; }
  .badge { display: inline-block; font-size: 11px; padding: 4px 10px; border-radius: 99px; background: rgba(59,130,246,0.2); color: #93c5fd; font-weight: 600; }
  .btn { width: 100%; padding: 13px; border: none; border-radius: 13px; font-size: 14px; font-weight: 700; cursor: pointer; transition: 0.15s; display: inline-flex; align-items: center; justify-content: center; gap: 8px; text-decoration: none; }
  .btn:active { transform: scale(0.98); }
  .btn-primary { background: linear-gradient(135deg, #2563eb, #3b82f6); color: #fff; }
  .btn-success { background: linear-gradient(135deg, #059669, #10b981); color: #fff; }
  .btn-danger { background: rgba(239,68,68,0.15); color: #f87171; border: 1px solid rgba(239,68,68,0.3); }
  .btn-ghost { background: var(--card2); color: var(--text); border: 1px solid var(--border); }
  .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; }
  input { width: 100%; padding: 13px 14px; background: #0c1220; border: 1px solid var(--border); border-radius: 12px; color: #fff; font-size: 14px; margin-bottom: 10px; outline: none; }
  input:focus { border-color: var(--primary); }
  .srv-btn { background: var(--card); border: 1px solid var(--border); border-radius: 14px; padding: 14px; text-align: left; color: #fff; cursor: pointer; display: flex; align-items: center; gap: 10px; font-weight: 700; font-size: 14px; }
  .srv-btn.active { border-color: var(--primary); background: rgba(59,130,246,0.12); }
  .country-row { display: flex; justify-content: space-between; align-items: center; background: var(--card2); border: 1px solid var(--border); padding: 12px 14px; border-radius: 14px; margin-bottom: 8px; }
  .price-tag { background: rgba(16,185,129,0.15); color: #34d399; padding: 6px 12px; border-radius: 10px; font-weight: 800; font-size: 13px; border: 1px solid rgba(16,185,129,0.3); cursor: pointer; }
  .nav { position: fixed; bottom: 0; left: 50%; transform: translateX(-50%); width: 100%; max-width: 480px; background: rgba(18,24,38,0.96); backdrop-filter: blur(14px); border-top: 1px solid var(--border); display: flex; justify-content: space-around; padding: 8px 4px 12px; z-index: 60; }
  .nav-item { background: none; border: none; color: var(--muted); font-size: 11px; font-weight: 600; display: flex; flex-direction: column; align-items: center; gap: 4px; cursor: pointer; padding: 4px 10px; }
  .nav-item.active { color: var(--primary); }
  .nav-icon { font-size: 19px; }
  .hidden { display: none !important; }
  .toast { position: fixed; top: 70px; left: 50%; transform: translateX(-50%); background: #1e293b; border: 1px solid var(--primary); color: #fff; padding: 10px 18px; border-radius: 12px; font-size: 13px; font-weight: 600; z-index: 100; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
  .otp-box { background: #090d16; border: 1px dashed var(--accent); padding: 12px; border-radius: 12px; text-align: center; font-size: 22px; font-weight: 800; letter-spacing: 3px; color: #34d399; margin: 10px 0; }
  .rule-item { margin-bottom: 12px; padding-bottom: 10px; border-bottom: 1px solid var(--border); }
  .rule-item h4 { font-size: 13px; color: #93c5fd; margin-bottom: 3px; }
  .rule-item p { font-size: 12px; color: var(--muted); line-height: 1.45; }
</style>
</head>
<body>

<div id="toast" class="toast hidden"></div>

<!-- AUTH SCREEN -->
<div id="auth-screen" class="container" style="padding-top: 40px;">
  <div style="text-align:center; margin-bottom:24px;">
    <div style="font-size:40px; margin-bottom:8px;">🌐</div>
    <h2 style="font-size:24px; font-weight:800;">WorldSIM <span style="color:#3b82f6;">Hub</span></h2>
    <p style="color:var(--muted); font-size:13px; margin-top:4px;">Instant Virtual Numbers & SMS Verification</p>
  </div>

  <div class="card">
    <div class="grid-2" style="margin-bottom:16px;">
      <button id="tab-login-btn" class="btn btn-primary" onclick="switchAuthTab('login')">Gmail Login</button>
      <button id="tab-signup-btn" class="btn btn-ghost" onclick="switchAuthTab('signup')">Create Account</button>
    </div>

    <div id="login-form">
      <input type="email" id="login-email" placeholder="Enter your Gmail (example@gmail.com)">
      <input type="password" id="login-pass" placeholder="Enter Password">
      <button class="btn btn-primary" onclick="doLogin()">🔐 Login to App</button>
    </div>

    <div id="signup-form" class="hidden">
      <input type="text" id="reg-name" placeholder="Your Name / Nickname">
      <input type="email" id="reg-email" placeholder="Your Gmail (example@gmail.com)">
      <input type="password" id="reg-pass" placeholder="Create Password">
      <input type="number" id="reg-tgid" placeholder="Old Telegram User ID (Optional - sync balance)">
      <button class="btn btn-success" onclick="doSignup()">✨ Create Account</button>
    </div>
  </div>
</div>

<!-- MAIN APP -->
<div id="main-app" class="hidden">
  <div class="header">
    <div class="brand">🌐 WorldSIM <span>Hub</span></div>
    <div class="bal-pill" id="top-bal">₹0.00</div>
  </div>

  <!-- HOME VIEW -->
  <div id="view-home" class="container">
    <div class="hero-card">
      <span class="badge">🔒 Verified Instant OTP Store</span>
      <div style="margin-top:10px; font-size:13px; color:var(--muted);" id="user-greeting">Welcome back!</div>
      <div class="hero-bal" id="hero-bal">₹0.00</div>
      <div style="font-size:12px; color:var(--muted); margin-bottom:14px;" id="user-meta">ID: —</div>
      <div class="grid-2">
        <button class="btn btn-primary" onclick="navTo('store')">🛒 Buy OTP</button>
        <button class="btn btn-success" onclick="navTo('recharge')">➕ Add Funds</button>
      </div>
    </div>

    <div class="card">
      <h3 style="font-size:15px; margin-bottom:12px;">⚡ Quick Platforms</h3>
      <div class="grid-2">
        <button class="srv-btn" onclick="openService('tg')">✈️ Telegram</button>
        <button class="srv-btn" onclick="openService('wa')">💬 WhatsApp</button>
        <button class="srv-btn" onclick="openService('go')">🌐 Google</button>
        <button class="srv-btn" onclick="openService('ig')">📸 Instagram</button>
      </div>
    </div>

    <div class="card" style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <div style="font-weight:700; font-size:14px;">🛠️ Need Help?</div>
        <div style="font-size:12px; color:var(--muted);">24/7 Support: @Worldsim_hub</div>
      </div>
      <a href="https://t.me/Worldsim_hub" target="_blank" class="btn btn-ghost" style="width:auto; padding:8px 14px;">Contact</a>
    </div>

    <button id="admin-nav-btn" class="btn btn-ghost hidden" style="margin-bottom:10px; border-color:#3b82f6;" onclick="navTo('admin')">👑 Open Admin Panel</button>
    <button class="btn btn-danger" onclick="doLogout()">🚪 Logout</button>
  </div>

  <!-- STORE VIEW -->
  <div id="view-store" class="container hidden">
    <div class="grid-3" style="margin-bottom:12px;">
      <button id="srv-tg" class="srv-btn active" onclick="openService('tg')">✈️ TG</button>
      <button id="srv-wa" class="srv-btn" onclick="openService('wa')">💬 WA</button>
      <button id="srv-go" class="srv-btn" onclick="openService('go')">🌐 GO</button>
    </div>
    <div class="grid-2" style="margin-bottom:12px;">
      <button id="srv-ig" class="srv-btn" onclick="openService('ig')">📸 Instagram</button>
      <button id="srv-fb" class="srv-btn" onclick="openService('fb')">📘 Facebook</button>
    </div>
    <input type="text" id="country-search" placeholder="🔍 Search country name..." oninput="renderCountries()">
    <div id="country-list"></div>
  </div>

  <!-- RECHARGE VIEW -->
  <div id="view-recharge" class="container hidden">
    <div class="card">
      <h3 style="font-size:16px; margin-bottom:6px;">🇮🇳 Instant UPI Deposit</h3>
      <p style="font-size:12px; color:var(--muted); margin-bottom:14px;">Minimum ₹10 • 2% Platform Fee • One UTR = One Credit</p>
      <div class="grid-3" style="margin-bottom:10px;">
        <button class="btn btn-ghost" onclick="createDeposit(10)">₹10</button>
        <button class="btn btn-ghost" onclick="createDeposit(50)">₹50</button>
        <button class="btn btn-ghost" onclick="createDeposit(100)">₹100</button>
        <button class="btn btn-ghost" onclick="createDeposit(250)">₹250</button>
        <button class="btn btn-ghost" onclick="createDeposit(500)">₹500</button>
        <button class="btn btn-ghost" onclick="createDeposit(1000)">₹1000</button>
      </div>
      <div style="display:flex; gap:8px;">
        <input type="number" id="custom-amt" placeholder="Custom ₹ (Min 10)" style="margin:0;">
        <button class="btn btn-primary" style="width:110px;" onclick="createDeposit(document.getElementById('custom-amt').value)">Pay</button>
      </div>
    </div>

    <div id="pay-box" class="card hidden">
      <div style="text-align:center;">
        <span class="badge" id="pay-order-id">Order #</span>
        <div style="margin:12px 0;"><img id="pay-qr" src="" style="width:190px; height:190px; border-radius:14px; background:#fff; padding:8px;"></div>
        <div style="font-size:13px; margin-bottom:12px;" id="pay-summary"></div>
        <a id="pay-link-btn" href="#" target="_blank" class="btn btn-primary" style="margin-bottom:12px;">💳 Pay Now (Instant UPI) ↗</a>
      </div>
      <input type="text" id="utr-input" maxlength="12" placeholder="Enter exact 12-digit UTR number">
      <button class="btn btn-success" onclick="verifyUtr()">✅ Verify 12-Digit UTR</button>
    </div>
  </div>

  <!-- ORDERS VIEW -->
  <div id="view-orders" class="container hidden">
    <h3 style="font-size:16px; margin-bottom:12px;">📑 Active & Recent Numbers</h3>
    <div id="orders-list"></div>
  </div>

  <!-- TERMS VIEW -->
  <div id="view-terms" class="container hidden">
    <div class="card">
      <h3 style="font-size:16px; margin-bottom:12px;">📋 Terms of Service</h3>
      <div class="rule-item"><h4>1. No Refunds</h4><p>All sales are final. No refunds under any circumstances.</p></div>
      <div class="rule-item"><h4>2. Sub-₹40 Rule</h4><p>Accounts priced below ₹40 carry no warranty for login failures or missing codes.</p></div>
      <div class="rule-item"><h4>3. No Re-logins</h4><p>Sessions are permanently closed after purchase. One login only.</p></div>
      <div class="rule-item"><h4>4. Premium Accounts</h4><p>Cheap quality accounts may last only 1–2 days. Buy at your own risk.</p></div>
      <div class="rule-item"><h4>5. No Longevity Guarantee</h4><p>We do not guarantee account lifespan, 2FA status or spam block status.</p></div>
      <div class="rule-item" style="border:none; margin:0; padding:0;"><h4>6. Liability</h4><p>Use at your own risk. Developed by - kissu (achi bachi)</p></div>
    </div>
  </div>

  <!-- ADMIN VIEW -->
  <div id="view-admin" class="container hidden">
    <div class="card">
      <h3 style="font-size:16px; margin-bottom:10px;">👑 Admin Balance Manager</h3>
      <input type="number" id="adm-uid" placeholder="User ID">
      <input type="number" id="adm-amt" placeholder="Amount (+ to add, - to cut)">
      <button class="btn btn-primary" onclick="adminUpdateBal()">Update User Balance</button>
    </div>
    <div class="card">
      <h3 style="font-size:15px; margin-bottom:10px;">👥 Registered Users</h3>
      <div id="admin-users-list" style="font-size:12px;">Loading...</div>
    </div>
  </div>

  <div class="nav">
    <button class="nav-item active" id="nav-home" onclick="navTo('home')"><span class="nav-icon">🏠</span>Home</button>
    <button class="nav-item" id="nav-store" onclick="navTo('store')"><span class="nav-icon">🛒</span>Buy OTP</button>
    <button class="nav-item" id="nav-recharge" onclick="navTo('recharge')"><span class="nav-icon">💳</span>Recharge</button>
    <button class="nav-item" id="nav-orders" onclick="navTo('orders')"><span class="nav-icon">📑</span>Orders</button>
    <button class="nav-item" id="nav-terms" onclick="navTo('terms')"><span class="nav-icon">📋</span>Terms</button>
  </div>
</div>

<script>
let state = { user: null, catalog: {}, orders: [], currentSrv: 'tg', activeDepOrderId: '' };

function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg; el.classList.remove('hidden');
  setTimeout(() => el.classList.add('hidden'), 3200);
}

function switchAuthTab(tab) {
  document.getElementById('login-form').classList.toggle('hidden', tab !== 'login');
  document.getElementById('signup-form').classList.toggle('hidden', tab !== 'signup');
  document.getElementById('tab-login-btn').className = tab === 'login' ? 'btn btn-primary' : 'btn btn-ghost';
  document.getElementById('tab-signup-btn').className = tab === 'signup' ? 'btn btn-success' : 'btn btn-ghost';
}

async function doLogin() {
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-pass').value;
  const r = await fetch('/api/auth/login', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({email, password}) }).then(x=>x.json());
  if (!r.ok) return toast(r.error);
  initApp();
}

async function doSignup() {
  const name = document.getElementById('reg-name').value;
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-pass').value;
  const tg_id = document.getElementById('reg-tgid').value;
  const r = await fetch('/api/auth/signup', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name, email, password, tg_id}) }).then(x=>x.json());
  if (!r.ok) return toast(r.error);
  toast('Account Created!');
  initApp();
}

async function doLogout() {
  await fetch('/api/auth/logout', { method:'POST' });
  location.reload();
}

async function initApp() {
  const r = await fetch('/api/me').then(x=>x.json());
  if (!r.ok) {
    document.getElementById('auth-screen').classList.remove('hidden');
    document.getElementById('main-app').classList.add('hidden');
    return;
  }
  state.user = r.user; state.catalog = r.catalog; state.orders = r.orders || [];
  document.getElementById('auth-screen').classList.add('hidden');
  document.getElementById('main-app').classList.remove('hidden');
  updateBalUI(r.user.balance);
  document.getElementById('user-greeting').textContent = `Welcome, ${r.user.name} (${r.user.email})`;
  document.getElementById('user-meta').textContent = `Account ID: ${r.user.uid} • Purchases: ${r.user.buys}`;
  if (r.user.is_admin) document.getElementById('admin-nav-btn').classList.remove('hidden');
  renderCountries(); renderOrders();
}

function updateBalUI(b) {
  const txt = `₹${Number(b).toFixed(2)}`;
  document.getElementById('top-bal').textContent = txt;
  document.getElementById('hero-bal').textContent = txt;
}

function navTo(view) {
  ['home','store','recharge','orders','terms','admin'].forEach(v => {
    document.getElementById('view-'+v).classList.toggle('hidden', v !== view);
    const n = document.getElementById('nav-'+v);
    if (n) n.classList.toggle('active', v === view);
  });
  if (view === 'admin') loadAdminUsers();
}

function openService(srv) {
  state.currentSrv = srv;
  ['tg','wa','go','ig','fb'].forEach(s => document.getElementById('srv-'+s).classList.toggle('active', s === srv));
  navTo('store');
  renderCountries();
}

function renderCountries() {
  const q = (document.getElementById('country-search').value || '').toLowerCase();
  const list = (state.catalog[state.currentSrv] || []).filter(c => c.name.toLowerCase().includes(q));
  document.getElementById('country-list').innerHTML = list.map(c => `
    <div class="country-row">
      <div><b>${c.flag} ${c.name}</b><div style="font-size:11px; color:var(--muted);">Instant SMS Delivery</div></div>
      <button class="price-tag" onclick="buyOtp('${state.currentSrv}','${c.id}')">Buy • ₹${c.price}</button>
    </div>
  `).join('') || '<div style="text-align:center; color:var(--muted); padding:20px;">No countries found</div>';
}

async function buyOtp(service, country_id) {
  toast('Allocating virtual number...');
  const r = await fetch('/api/otp/buy', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({service, country_id}) }).then(x=>x.json());
  if (!r.ok) return toast(r.error);
  updateBalUI(r.new_balance);
  state.orders.unshift(r.order);
  renderOrders(); navTo('orders');
  toast('Number Ready! Waiting for OTP...');
}

function renderOrders() {
  const el = document.getElementById('orders-list');
  if (!state.orders.length) { el.innerHTML = '<div class="card" style="text-align:center; color:var(--muted);">No orders yet</div>'; return; }
  el.innerHTML = state.orders.map(o => {
    const left = Math.max(0, 1200 - Math.floor(Date.now()/1000 - o.created_at));
    const mins = String(Math.floor(left/60)).padStart(2,'0');
    const secs = String(left%60).padStart(2,'0');
    return `
    <div class="card">
      <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
        <b>${o.service} • ${o.country}</b>
        <span class="badge">${o.status === 'waiting' ? `⏳ ${mins}:${secs}` : o.status.toUpperCase()}</span>
      </div>
      <div style="font-size:16px; font-weight:800; color:#93c5fd; margin-bottom:6px;">+${o.phone}</div>
      ${o.otp ? `<div class="otp-box">${o.otp}</div>` : ''}
      ${o.status === 'waiting' ? `<button class="btn btn-danger" style="margin-top:8px;" onclick="cancelOrder('${o.activation_id}')">❌ Cancel & Refund ₹${o.price}</button>` : ''}
    </div>`;
  }).join('');
}

async function cancelOrder(actId) {
  const r = await fetch('/api/otp/cancel/' + actId, { method:'POST' }).then(x=>x.json());
  if (!r.ok) return toast(r.error);
  updateBalUI(r.new_balance);
  const o = state.orders.find(x => x.activation_id === actId);
  if (o) o.status = 'cancelled';
  renderOrders(); toast('Order cancelled & refunded!');
}

setInterval(async () => {
  if (!state.user) return;
  let changed = false;
  for (let o of state.orders) {
    if (o.status === 'waiting') {
      changed = true;
            const r = await fetch('/api/otp/status/' + o.activation_id).then(x=>x.json());
      if (r.ok && r.order) {
        Object.assign(o, r.order);
        if (r.new_balance !== undefined) updateBalUI(r.new_balance);
        if (o.status === 'received') toast('✅ OTP Received: ' + o.otp);
      }
    }
  }
  if (changed) renderOrders();
}, 4000);

async function createDeposit(amount) {
  if (!amount || Number(amount) < 10) return toast('Minimum deposit ₹10 hai!');
  toast('Generating payment link...');
  const r = await fetch('/api/deposit/create', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({amount}) }).then(x=>x.json());
  if (!r.ok) return toast(r.error);
  state.activeDepOrderId = r.order.order_id;
  document.getElementById('pay-box').classList.remove('hidden');
  document.getElementById('pay-order-id').textContent = 'Txn ID: ' + r.order.order_id;
  document.getElementById('pay-qr').src = r.order.qr_url;
  document.getElementById('pay-link-btn').href = r.order.payment_url;
  document.getElementById('pay-summary').innerHTML = `Pay: <b>₹${r.order.amount}</b> • Fee (2%): -₹${r.order.fee} • Credit: <b style="color:#34d399;">₹${r.order.net_credit}</b>`;
}

async function verifyUtr() {
  const utr = document.getElementById('utr-input').value.trim();
  const r = await fetch('/api/deposit/verify', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({order_id: state.activeDepOrderId, utr}) }).then(x=>x.json());
  if (!r.ok) return toast(r.error);
  updateBalUI(r.new_balance);
  document.getElementById('pay-box').classList.add('hidden');
  document.getElementById('utr-input').value = '';
  toast(`✅ ₹${r.credited} Wallet me add ho gaye!`);
}

async function loadAdminUsers() {
  const r = await fetch('/api/admin/users').then(x=>x.json());
  if (!r.ok) return;
  document.getElementById('admin-users-list').innerHTML = r.users.map(u => `
    <div style="padding:8px 0; border-bottom:1px solid var(--border);">
      <b>${u.nickname || u.email || 'User'}</b> (ID: <code>${u.uid}</code>)<br>
      Bal: <b style="color:#34d399;">₹${u.balance}</b> | Buys: ${u.buys} | ${u.email || u.username}
    </div>
  `).join('');
}

async function adminUpdateBal() {
  const target_uid = document.getElementById('adm-uid').value;
  const delta = document.getElementById('adm-amt').value;
  const r = await fetch('/api/admin/balance', { method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({target_uid, delta}) }).then(x=>x.json());
  if (r.ok) { toast('Balance Updated: ₹' + r.new_balance); loadAdminUsers(); }
}

initApp();
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(APP_HTML)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
# --- END OF PART 5 ---
