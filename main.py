import telebot
import random
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import threading
from datetime import datetime
import pytz
import ably
from ably import AblyRest

# -----------------------------
# Telegram Bot Setup
# -----------------------------
BOT_TOKEN = "8322920563:AAFnm1-xzsArXQnRBJNa8I3uiH-nqL5goPY"
bot = telebot.TeleBot(BOT_TOKEN)

# -----------------------------
# Ably Setup
# -----------------------------
ABLY_API_KEY = "RL1tBQ.35M5xw:mxRYIB9D0t2q-3BUcO2Gab1SbtE7oy8QA_S1CkWlPps"  # Replace with your Ably API Key
ably_client = AblyRest(ABLY_API_KEY)
ably_channel = ably_client.channels.get("daily-code")

# -----------------------------
# Daily Code Logic
# -----------------------------
daily_code_data = {"code": None, "last_generated": None}
NIGERIA_TZ = pytz.timezone("Africa/Lagos")

def get_daily_code():
    now = datetime.now(NIGERIA_TZ)
    today_3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

    # Generate new code if none exists or last_generated < today 3PM and now >= 3PM
    if (daily_code_data["code"] is None or
        daily_code_data["last_generated"] < today_3pm <= now):
        new_code = str(random.randint(100000, 999999))
        daily_code_data["code"] = new_code
        daily_code_data["last_generated"] = now

        # Publish new code to Ably
        ably_channel.publish("update", {"code": new_code})

    return daily_code_data["code"]

# -----------------------------
# Telegram Command
# -----------------------------
@bot.message_handler(commands=['start'])
def send_code(message):
    code = get_daily_code()
    
    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        text=f"Copy Code: {code}",
        url=f"tg://msg_url?text={code}"
    )
    markup.add(button)

    bot.send_message(
        message.chat.id,
        f"Welcome! Here is today's 6-digit code:\n\n{code}\n\nTap the button below to copy it.",
        reply_markup=markup
    )

# -----------------------------
# Flask Web Server
# -----------------------------
app = Flask('')
CORS(app)  # Optional if you want to fetch via /daily-code

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/daily-code', methods=['GET'])
def daily_code_endpoint():
    return jsonify({"code": get_daily_code()})

# Serve HTML page from /static
@app.route('/app')
def serve_html():
    return send_from_directory('static', 'index.html')

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# -----------------------------
# Start Flask + Telegram Bot
# -----------------------------
threading.Thread(target=run_flask).start()
bot.infinity_polling()
