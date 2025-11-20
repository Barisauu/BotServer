import random
from datetime import datetime
import pytz
import threading
from flask import Flask
from ably import AblyRest, AblyRealtime
import telebot

# -------------------------
# SETTINGS
# -------------------------

BOT_TOKEN = "8322920563:AAFnm1-xzsArXQnRBJNa8I3uiH-nqL5goPY"

ABLY_KEY = "RL1tBQ.35M5xw:mxRYIB9D0t2q-3BUcO2Gab1SbtE7oy8QA_S1CkWlPps"
CHANNEL_NAME = "daily-code"

tz = pytz.timezone("Africa/Lagos")
current_code = None
last_generated_date = None

# -------------------------
# DAILY CODE LOGIC
# -------------------------

def get_daily_code():
    global current_code, last_generated_date

    now = datetime.now(tz)

    if current_code is None:
        current_code = str(random.randint(100000, 999999))
        last_generated_date = now.date()
        return current_code

    if now.date() != last_generated_date and now.hour >= 15:
        current_code = str(random.randint(100000, 999999))
        last_generated_date = now.date()

    return current_code


# -------------------------
# ABLY REALTIME LISTENER (HTML → SERVER)
# -------------------------

ably_r = AblyRealtime(ABLY_KEY)
ably_rest = AblyRest(ABLY_KEY)
channel = ably_r.channels.get(CHANNEL_NAME)

def on_message(msg):
    if msg.name == "request-code":
        code = get_daily_code()
        ably_rest.channels.get(CHANNEL_NAME).publish("return-code", {"code": code})

channel.subscribe(on_message)


# -------------------------
# TELEGRAM BOT
# -------------------------

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    code = get_daily_code()
    bot.send_message(
        message.chat.id,
        f"Your Daily Universal Code:\n\n🔐 *{code}*\n\nThis code updates daily at *3PM Nigeria time*.",
        parse_mode='Markdown'
    )


def run_bot():
    bot.infinity_polling()


# -------------------------
# FLASK FOR RENDER
# -------------------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Bot + Ably Daily Code Server Running Successfully!"


def run_flask():
    app.run(host="0.0.0.0", port=10000)


# -------------------------
# START EVERYTHING
# -------------------------

threading.Thread(target=run_flask).start()
threading.Thread(target=run_bot).start()
