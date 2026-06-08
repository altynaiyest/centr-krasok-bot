import os
import threading
from flask import Flask
from bot import main

app = Flask(__name__)

bot_thread = threading.Thread(target=main)

@app.route('/')
def home():
    return "Bot is running!", 200

@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    bot_thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))