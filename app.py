import os
from flask import Flask, send_file

try:
    from bot import app
except Exception:
    app = Flask(__name__)

def find_index_html():
    for root, dirs, files in os.walk("."):
        if "index.html" in files:
            return os.path.join(root, "index.html")
    return None

@app.route("/")
@app.route("/<path:subpath>")
def catch_all(subpath=""):
    if subpath.startswith("api/"):
        return {"ok": False, "error": "API route not loaded"}, 404
    html_path = find_index_html()
    if html_path:
        return send_file(html_path)
    return "<h1>Kissu Num Services</h1><p>index.html file GitHub repo me nahi mili!</p>", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
