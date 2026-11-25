import os
from bot import app

@app.route("/")
def index():
    files = os.listdir(".")
    if "index.html" in files:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return f"Files in folder: {files}", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    
