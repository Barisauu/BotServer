import telebot
import random

BOT_TOKEN = "8322920563:AAFnm1-xzsArXQnRBJNa8I3uiH-nqL5goPY"
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_code(message):
    code = str(random.randint(100000, 999999))

    markup = telebot.types.InlineKeyboardMarkup()
    button = telebot.types.InlineKeyboardButton(
        text=f"Copy Code: {code}",
        url=f"tg://msg_url?text={code}"
    )
    markup.add(button)

    bot.send_message(
        message.chat.id, 
        f"Welcome! Here is your 6-digit code:\n\n{code}\n\nTap the button below to copy it.",
        reply_markup=markup
    )

bot.infinity_polling()
