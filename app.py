from bot import app

app.url_map._rules = [r for r in app.url_map._rules if r.rule != '/']
app.url_map._rules_by_endpoint.pop('index', None)
app.url_map._rules_by_endpoint.pop('home_page', None)

@app.route("/")
def serve_kissu_app():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
