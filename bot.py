import os
import re
import time
import uuid
import hashlib
import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify, session

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "kissu_num_super_secret_2026_key")

DATABASE_URL = os.environ.get("DATABASE_URL")
SASTA_API_KEY = "stp_4905928f4de82481bad70ffd7d8da6b59e82e625396bebc3"
SASTA_BASE_URL = "https://sastasms.com/stubs/handler_api.php"

ZAPUPI_TOKEN = os.environ.get("ZAPUPI_TOKEN", "")
ZAPUPI_SECRET = os.environ.get("ZAPUPI_SECRET", "")

SECRET_ADMIN_EMAIL = "acchi.bachii@gmail.com"
SECRET_ADMIN_ID = 8539777823
SUPPORT_HANDLE = "@kissu_num"
SUPPORT_ID = "8160944561"

def get_db_conn():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    if not DATABASE_URL:
        return
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS worldsim_users (
                    user_id BIGINT PRIMARY KEY,
                    balance NUMERIC(10, 2) DEFAULT 0.00,
                    referred_by BIGINT,
                    email TEXT UNIQUE,
                    password_hash TEXT,
                    full_name TEXT
                );
            """)
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS email TEXT UNIQUE;")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS password_hash TEXT;")
            cur.execute("ALTER TABLE worldsim_users ADD COLUMN IF NOT EXISTS full_name TEXT;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS used_utrs (
                    utr TEXT PRIMARY KEY,
                    user_id BIGINT,
                    amount NUMERIC(10, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS verified_orders (
                    order_id TEXT PRIMARY KEY,
                    user_id BIGINT,
                    amount NUMERIC(10, 2),
                    status TEXT DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            cur.execute("""
                INSERT INTO worldsim_users (user_id, balance, email, full_name)
                VALUES (%s, 0.00, %s, 'Kissu Admin')
                ON CONFLICT (user_id) DO UPDATE SET email = EXCLUDED.email;
            """, (SECRET_ADMIN_ID, SECRET_ADMIN_EMAIL))
        conn.commit()
    finally:
        conn.close()

try:
    init_db()
except Exception as e:
    print("DB Init Warning:", e)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(("kissu_salt_" + pw).encode()).hexdigest()

def is_admin(uid) -> bool:
    try:
        return int(uid) == SECRET_ADMIN_ID
    except Exception:
        return False
COUNTRIES = [
    {"id": "6", "name": "Indonesia", "flag": "🇮🇩", "mult": 1.0},
    {"id": "151", "name": "Chile", "flag": "🇨🇱", "mult": 1.1},
    {"id": "187", "name": "USA-2", "flag": "🇺🇸", "mult": 1.25},
    {"id": "33", "name": "Colombia", "flag": "🇨🇴", "mult": 1.1},
    {"id": "31", "name": "South Africa", "flag": "🇿🇦", "mult": 1.15},
    {"id": "36", "name": "Canada", "flag": "🇨🇦", "mult": 1.3},
    {"id": "66", "name": "Pakistan", "flag": "🇵🇰", "mult": 1.05},
    {"id": "22", "name": "India", "flag": "🇮🇳", "mult": 1.2}
]

SERVICES_CONFIG = {
    "tg": {"name": "Telegram", "icon": "✈️", "base": 25, "margin": 10},
    "wa": {"name": "WhatsApp", "icon": "💬", "base": 35, "margin": 0},
    "go": {"name": "Google / Gmail", "icon": "📧", "base": 18, "margin": 0},
    "ig": {"name": "Instagram", "icon": "📸", "base": 16, "margin": 0},
    "fb": {"name": "Facebook", "icon": "📘", "base": 15, "margin": 0},
    "tw": {"name": "Twitter / X", "icon": "🐦", "base": 14, "margin": 5},
    "fu": {"name": "Snapchat", "icon": "👻", "base": 15, "margin": 5},
    "am": {"name": "Amazon", "icon": "📦", "base": 16, "margin": 5},
    "xi": {"name": "Flipkart", "icon": "🛍️", "base": 15, "margin": 5},
    "ts": {"name": "PayPal", "icon": "💳", "base": 22, "margin": 5},
    "ds": {"name": "Discord", "icon": "🎮", "base": 14, "margin": 5},
    "nf": {"name": "Netflix", "icon": "🎬", "base": 20, "margin": 5},
    "mm": {"name": "Microsoft", "icon": "🪟", "base": 15, "margin": 5},
    "ub": {"name": "Uber", "icon": "🚕", "base": 15, "margin": 5},
    "oi": {"name": "Tinder", "icon": "🔥", "base": 18, "margin": 5}
}

def get_full_catalog():
    catalog = {}
    for code, cfg in SERVICES_CONFIG.items():
        items = []
        for c in COUNTRIES:
            price = round((cfg["base"] * c["mult"]) + cfg["margin"], 2)
            items.append({
                "id": c["id"],
                "country_id": c["id"],
                "name": c["name"],
                "country": c["name"],
                "country_name": c["name"],
                "flag": c["flag"],
                "price": price
            })
        catalog[code] = items
    return catalog

@app.route("/api/me")
def api_me():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False})
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT user_id, balance, email, full_name FROM worldsim_users WHERE user_id = %s", (int(uid),))
            u = cur.fetchone()
            if not u:
                session.clear()
                return jsonify({"ok": False})
            name = u["full_name"] or "Kissu"
            return jsonify({
                "ok": True,
                "user": {
                    "id": u["user_id"],
                    "user_id": u["user_id"],
                    "name": name,
                    "full_name": name,
                    "balance": float(u["balance"]),
                    "purchases": 0,
                    "email": u["email"],
                    "is_admin": is_admin(u["user_id"]),
                    "support": SUPPORT_HANDLE
                }
            })
    finally:
        conn.close()

@app.route("/api/auth/signup", methods=["POST"])
def api_signup():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    full_name = (data.get("full_name") or "Kissu").strip()
    old_tg_id = str(data.get("old_tg_id") or "").strip()

    if not email or "@" not in email or len(password) < 4:
        return jsonify({"ok": False, "error": "Valid email aur kam se kam 4 digit password daalein."})

    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            if email == SECRET_ADMIN_EMAIL:
                cur.execute("""
                    UPDATE worldsim_users SET password_hash = %s, full_name = %s
                    WHERE user_id = %s RETURNING user_id
                """, (hash_pw(password), full_name or "Kissu Admin", SECRET_ADMIN_ID))
                conn.commit()
                session["uid"] = SECRET_ADMIN_ID
                return jsonify({"ok": True})

            cur.execute("SELECT user_id FROM worldsim_users WHERE email = %s", (email,))
            if cur.fetchone():
                return jsonify({"ok": False, "error": "Yeh email pehle se registered hai, Login karein."})

            target_uid = None
            if old_tg_id.isdigit():
                cur.execute("SELECT user_id, email FROM worldsim_users WHERE user_id = %s", (int(old_tg_id),))
                existing_tg = cur.fetchone()
                if existing_tg and not existing_tg["email"]:
                    target_uid = int(old_tg_id)

            if target_uid:
                cur.execute("""
                    UPDATE worldsim_users SET email = %s, password_hash = %s, full_name = %s
                    WHERE user_id = %s
                """, (email, hash_pw(password), full_name, target_uid))
            else:
                target_uid = int(str(int(time.time() * 1000))[-10:])
                cur.execute("""
                    INSERT INTO worldsim_users (user_id, balance, email, password_hash, full_name)
                    VALUES (%s, 0.00, %s, %s, %s)
                """, (target_uid, email, hash_pw(password), full_name))
        conn.commit()
        session["uid"] = target_uid
        return jsonify({"ok": True})
    finally:
        conn.close()

@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.json or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT user_id, password_hash FROM worldsim_users WHERE email = %s", (email,))
            u = cur.fetchone()
            if not u or u["password_hash"] != hash_pw(password):
                return jsonify({"ok": False, "error": "Galat Email ya Password."})
            session["uid"] = int(u["user_id"])
            return jsonify({"ok": True})
    finally:
        conn.close()

@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})
@app.route("/api/catalog")
def api_catalog():
    services = [{"code": k, "id": k, "name": v["name"], "icon": v["icon"]} for k, v in SERVICES_CONFIG.items()]
    full_cat = get_full_catalog()
    return jsonify({
        "ok": True,
        "services": services,
        "countries": COUNTRIES,
        "catalog": full_cat,
        "prices": full_cat
    })

@app.route("/api/otp/buy", methods=["POST"])
def api_otp_buy():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False, "error": "Pehle login karein."})
    uid = int(uid)
    data = request.json or {}
    service = str(data.get("service") or "")
    country_id = str(data.get("country_id") or data.get("country") or "")

    catalog = get_full_catalog().get(service, [])
    country_item = next((c for c in catalog if c["country_id"] == country_id), None)
    if not country_item:
        return jsonify({"ok": False, "error": "Invalid service ya country."})

    price = float(country_item["price"])
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT balance FROM worldsim_users WHERE user_id = %s FOR UPDATE", (uid,))
            r = cur.fetchone()
            bal = float(r[0]) if r else 0.0
            if bal < price:
                return jsonify({"ok": False, "error": f"Insufficient balance! ₹{price} chahiye."})

            resp = requests.get(SASTA_BASE_URL, params={
                "api_key": SASTA_API_KEY,
                "action": "getNumber",
                "service": service,
                "country": country_id
            }, timeout=15).text.strip()

            if not resp.startswith("ACCESS_NUMBER:"):
                return jsonify({"ok": False, "error": f"Stock unavailable ({resp}). Paise nahi kate hain."})

            _, activation_id, phone_number = resp.split(":", 2)
            cur.execute("UPDATE worldsim_users SET balance = balance - %s WHERE user_id = %s RETURNING balance", (price, uid))
            new_bal = float(cur.fetchone()[0])
        conn.commit()
        return jsonify({
            "ok": True,
            "activation_id": activation_id,
            "number": phone_number,
            "price": price,
            "new_balance": new_bal
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"ok": False, "error": str(e)})
    finally:
        conn.close()

@app.route("/api/otp/status")
def api_otp_status():
    act_id = request.args.get("id", "")
    resp = requests.get(SASTA_BASE_URL, params={
        "api_key": SASTA_API_KEY,
        "action": "getStatus",
        "id": act_id
    }, timeout=15).text.strip()
    if resp.startswith("STATUS_OK:"):
        return jsonify({"ok": True, "status": "RECEIVED", "code": resp.split(":", 1)[1]})
    return jsonify({"ok": True, "status": resp})

@app.route("/api/otp/cancel", methods=["POST"])
def api_otp_cancel():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False, "error": "Unauthorized"})
    data = request.json or {}
    act_id = str(data.get("id") or "")
    price = float(data.get("price") or 0)
    resp = requests.get(SASTA_BASE_URL, params={
        "api_key": SASTA_API_KEY,
        "action": "setStatus",
        "status": "8",
        "id": act_id
    }, timeout=15).text.strip()
    if "ACCESS_CANCEL" in resp:
        conn = get_db_conn()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE worldsim_users SET balance = balance + %s WHERE user_id = %s RETURNING balance", (price, int(uid)))
                new_bal = float(cur.fetchone()[0])
            conn.commit()
            return jsonify({"ok": True, "new_balance": new_bal})
        finally:
            conn.close()
    return jsonify({"ok": False, "error": resp})

@app.route("/api/recharge/create", methods=["POST"])
def api_recharge_create():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False, "error": "Login required"})
    amount = float((request.json or {}).get("amount") or 0)
    if amount < 10:
        return jsonify({"ok": False, "error": "Minimum recharge ₹10 hai."})
    fee = round(amount * 0.02, 2)
    total_payable = round(amount + fee, 2)
    order_id = "KISSU" + uuid.uuid4().hex[:10].upper()

    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO verified_orders (order_id, user_id, amount, status) VALUES (%s, %s, %s, 'PENDING')", (order_id, int(uid), amount))
        conn.commit()
    finally:
        conn.close()

    pay_url = ""
    if ZAPUPI_TOKEN and ZAPUPI_SECRET:
        try:
            r = requests.post("https://api.zapupi.com/api/create-order", data={
                "token_key": ZAPUPI_TOKEN,
                "secret_key": ZAPUPI_SECRET,
                "amount": str(total_payable),
                "order_id": order_id,
                "custumer_mobile": "9999999999",
                "redirect_url": request.host_url
            }, timeout=15).json()
            pay_url = r.get("payment_url") or r.get("data", {}).get("payment_url") or ""
        except Exception:
            pass

    return jsonify({
        "ok": True,
        "order_id": order_id,
        "wallet_credit": amount,
        "fee": fee,
        "total_payable": total_payable,
        "payment_url": pay_url
    })

@app.route("/api/recharge/verify-utr", methods=["POST"])
def api_verify_utr():
    uid = session.get("uid")
    if not uid:
        return jsonify({"ok": False, "error": "Login required"})
    data = request.json or {}
    utr = (data.get("utr") or "").strip()
    order_id = (data.get("order_id") or "").strip()

    if not re.fullmatch(r"\d{12}", utr):
        return jsonify({"ok": False, "error": "Exact 12-digit UTR number daalein."})

    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT utr FROM used_utrs WHERE utr = %s", (utr,))
            if cur.fetchone():
                return jsonify({"ok": False, "error": "Yeh UTR pehle hi use ho chuka hai!"})

            cur.execute("SELECT amount, status FROM verified_orders WHERE order_id = %s AND user_id = %s", (order_id, int(uid)))
            ord_row = cur.fetchone()
            if not ord_row or ord_row["status"] == "PAID":
                return jsonify({"ok": False, "error": "Invalid ya already verified order."})

            credit_amt = float(ord_row["amount"])
            cur.execute("INSERT INTO used_utrs (utr, user_id, amount) VALUES (%s, %s, %s)", (utr, int(uid), credit_amt))
            cur.execute("UPDATE verified_orders SET status = 'PAID' WHERE order_id = %s", (order_id,))
            cur.execute("UPDATE worldsim_users SET balance = balance + %s WHERE user_id = %s RETURNING balance", (credit_amt, int(uid)))
            new_bal = float(cur.fetchone()["balance"])
        conn.commit()
        return jsonify({"ok": True, "new_balance": new_bal, "credited": credit_amt})
    finally:
        conn.close()

@app.route("/api/admin/stats")
def api_admin_stats():
    if not is_admin(session.get("uid")):
        return jsonify({"ok": False, "error": "Forbidden"}), 403
    conn = get_db_conn()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS total_users, COALESCE(SUM(balance), 0) AS total_bal FROM worldsim_users")
            s = cur.fetchone()
            cur.execute("SELECT user_id, email, full_name, balance FROM worldsim_users ORDER BY balance DESC LIMIT 25")
            users = cur.fetchall()
        sasta_bal = "0"
        try:
            sasta_bal = requests.get(SASTA_BASE_URL, params={"api_key": SASTA_API_KEY, "action": "getBalance"}, timeout=10).text
        except Exception:
            pass
        return jsonify({
            "ok": True,
            "total_users": s["total_users"],
            "total_user_balance": float(s["total_bal"]),
            "sasta_api_balance": sasta_bal,
            "users": [dict(u, balance=float(u["balance"])) for u in users]
        })
    finally:
        conn.close()

@app.route("/api/admin/adjust-balance", methods=["POST"])
def api_admin_adjust():
    if not is_admin(session.get("uid")):
        return jsonify({"ok": False, "error": "Forbidden"}), 403
    data = request.json or {}
    target = (data.get("target") or "").strip().lower()
    amount = float(data.get("amount") or 0)
    conn = get_db_conn()
    try:
        with conn.cursor() as cur:
            if target.isdigit():
                cur.execute("UPDATE worldsim_users SET balance = balance + %s WHERE user_id = %s RETURNING user_id, balance", (amount, int(target)))
            else:
                cur.execute("UPDATE worldsim_users SET balance = balance + %s WHERE email = %s RETURNING user_id, balance", (amount, target))
            row = cur.fetchone()
            if not row:
                return jsonify({"ok": False, "error": "User nahi mila."})
        conn.commit()
        return jsonify({"ok": True, "user_id": row[0], "new_balance": float(row[1])})
    finally:
        conn.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
