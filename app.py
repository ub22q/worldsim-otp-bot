from bot import app

@app.route("/")
def home_page():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
