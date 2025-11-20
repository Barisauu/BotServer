import telebot
import random
from datetime import datetime, timedelta
import pytz

BOT_TOKEN = "8322920563:AAFnm1-xzsArXQnRBJNa8I3uiH-nqL5goPY"
bot = telebot.TeleBot(BOT_TOKEN)

# Global storage for the daily code
daily_code_data = {
    "code": None,
    "last_generated": None
}

NIGERIA_TZ = pytz.timezone("Africa/Lagos")

def get_daily_code():
    now = datetime.now(NIGERIA_TZ)
    today_3pm = now.replace(hour=15, minute=0, second=0, microsecond=0)

    # If code is None or last_generated < today 3pm and now >= 3pm, generate new code
    if (daily_code_data["code"] is None or
        daily_code_data["last_generated"] < today_3pm <= now):
        new_code = str(random.randint(100000, 999999))
        daily_code_data["code"] = new_code
        daily_code_data["last_generated"] = now
    return daily_code_data["code"]

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
        f"Welcome! Here is today’s 6-digit code:\n\n{code}\n\nTap the button below to copy it.",
        reply_markup=markup
    )

bot.infinity_polling()
