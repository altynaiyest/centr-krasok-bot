import os
import asyncio
from flask import Flask
import threading
from bot import main
 
app = Flask(__name__)
 
@app.route('/')
def home():
    return "Bot is running!", 200
 
@app.route('/health')
def health():
    return "OK", 200
 
def run_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
 
if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
