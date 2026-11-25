import os
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

try:
    import bot
    app.secret_key = bot.app.secret_key
    for rule in bot.app.url_map.iter_rules():
        if rule.rule.startswith("/api/"):
            app.add_url_rule(
                rule.rule,
                endpoint=rule.endpoint,
                view_func=bot.app.view_functions[rule.endpoint],
                methods=rule.methods
            )
except Exception as e:
    print("Bot import note:", e)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/api/bg-images")
def list_bg_images():
    imgs = sorted([f for f in os.listdir(BASE_DIR) if f.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))])
    return jsonify({"ok": True, "images": imgs})

@app.route("/img/<path:filename>")
def serve_img(filename):
    return send_from_directory(BASE_DIR, filename)

@app.route("/")
@app.route("/index.html")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.errorhandler(404)
def fallback_404(e):
    if request.path.startswith("/api/"):
        return {"ok": False, "error": "API endpoint not found"}, 404
    return send_from_directory(BASE_DIR, "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
