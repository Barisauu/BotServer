import telebot
import random
from flask import Flask, jsonify
from flask_cors import CORS

CORS(app, resources={r"/*": {"origins": "*"}})
import threading
from datetime import datetime
import pytz

# -----------------------------
# Telegram Bot Setup
# -----------------------------
BOT_TOKEN = "8322920563:AAFnm1-xzsArXQnRBJNa8I3uiH-nqL5goPY"
bot = telebot.TeleBot(BOT_TOKEN)

# -----------------------------
# Daily Code Logic
# -----------------------------
daily_code_data = {"code": None, "last_generated": None}
NIGERIA_TZ = pytz.timezone("Africa/Lagos")

def get_daily_code():
    now = datetime.now(NIGERIA_TZ)
    today_3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

    # Generate a new code if none exists or last_generated < today 3PM and now >= 3PM
    if (daily_code_data["code"] is None or
        daily_code_data["last_generated"] < today_3pm <= now):
        new_code = str(random.randint(100000, 999999))
        daily_code_data["code"] = new_code
        daily_code_data["last_generated"] = now

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
# Flask Web Server with CORS
# -----------------------------
app = Flask('')
CORS(app)  # Enable CORS for all origins

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/daily-code', methods=['GET'])
def daily_code_endpoint():
    return jsonify({"code": get_daily_code()})

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# -----------------------------
# Start Flask + Telegram Bot
# -----------------------------
threading.Thread(target=run_flask).start()
bot.infinity_polling()
