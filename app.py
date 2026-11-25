from flask import Flask, send_file
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from bot import app as backend_app

front = Flask(__name__)

@front.route("/")
@front.route("/index.html")
def serve_home():
    return send_file("index.html")

app = DispatcherMiddleware(backend_app, {
    "/": front
})
