from bot import app as flask_app

def app(environ, start_response):
    path = environ.get("PATH_INFO", "")
    if path in ("", "/", "/index.html"):
        with open("index.html", "rb") as f:
            html = f.read()
        start_response("200 OK", [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(html)))
        ])
        return [html]
    return flask_app(environ, start_response)
    
