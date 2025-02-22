from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run():
    app.run(host="0.0.0.0", port=5002)

def keep_alive():
    thread = Thread(target=run)
    thread.start()
