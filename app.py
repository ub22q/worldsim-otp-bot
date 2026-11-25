from bot import app as base_app

# Purane conflicting '/' route ko clear karke index.html load karein
base_app.view_functions['home_page'] = lambda: open("index.html", "r", encoding="utf-8").read()
base_app.add_url_rule("/", endpoint="home_page", view_func=base_app.view_functions['home_page'])

app = base_app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
    
