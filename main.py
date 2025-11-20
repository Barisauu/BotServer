import random
import threading
import requests
from datetime import datetime
import pytz
from flask import Flask
import telebot

# ----------------------------------------------------
# SETTINGS
# ----------------------------------------------------

BOT_TOKEN = "8322920563:AAFnm1-xzsArXQnRBJNa8I3uiH-nqL5goPY"
WEBHOOK_URL = "https://your-webhook-here.com/receiver"   # <<< REPLACE THIS

tz = pytz.timezone("Africa/Lagos")

current_code = None
last_generated_date = None


# ----------------------------------------------------
# DAILY CODE GENERATOR (3PM NIGERIA TIME)
# ----------------------------------------------------

def get_daily_code():
    global current_code, last_generated_date

    now = datetime.now(tz)

    # First-time generation
    if current_code is None:
        current_code = str(random.randint(100000, 999999))
        last_generated_date = now.date()
        return current_code

    # New day + past 3pm → generate new code
    if now.date() != last_generated_date and now.hour >= 15:
        current_code = str(random.randint(100000, 999999))
        last_generated_date = now.date()

    return current_code


# ----------------------------------------------------
# SEND CODE TO YOUR WEBHOOK
# ----------------------------------------------------

def send_to_webhook(code):
    try:
        requests.post(WEBHOOK_URL, json={"code": code}, timeout=5)
    except Exception as e:
        print("Webhook error:", e)


# ----------------------------------------------------
# TELEGRAM BOT
# ----------------------------------------------------

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def start_cmd(message):
    code = get_daily_code()

    # Send to Telegram
    bot.send_message(
        message.chat.id,
        f"Your Daily Universal Code:\n\n🔐 *{code}*\n\nUpdates daily at 3PM Nigeria time.",
        parse_mode='Markdown'
    )

    # Also send to webhook
    send_to_webhook(code)


def run_bot():
    bot.infinity_polling()


# ----------------------------------------------------
# FLASK SERVER FOR RENDER
# ----------------------------------------------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Telegram Bot Daily Code Server Running Successfully!"


def run_flask():
    app.run(host="0.0.0.0", port=10000)


# ----------------------------------------------------
# START BOT + FLASK IN PARALLEL
# ----------------------------------------------------

threading.Thread(target=run_flask).start()
threading.Thread(target=run_bot).start()
