import os
from flask import Flask, send_from_directory, request

app = Flask(__name__)

# bot.py ke sabhi API routes aur secret key ko yahan copy karein
try:
    import bot
    app.secret_key = bot.app.secret_key
    for rule in bot.app.url_map.iter_rules():
        if rule.rule.startswith("/api/"):
            view_func = bot.app.view_functions[rule.endpoint]
            app.add_url_rule(rule.rule, endpoint=rule.endpoint, view_func=view_func, methods=rule.methods)
except Exception as e:
    print("Bot import note:", e)

@app.route("/")
@app.route("/index.html")
def home():
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")

@app.errorhandler(404)
def fallback_404(e):
    if request.path.startswith("/api/"):
        return {"ok": False, "error": "API endpoint not found"}, 404
    return send_from_directory(os.path.dirname(os.path.abspath(__file__)), "index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
