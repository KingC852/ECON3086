
import telebot
from telebot import types


BOT_TOKEN = '6120420567:AAHwSVOlFi333PdvhrFmV3Mai4lc0nGyaVY'

# Create an instance of the Telegram bot
bot = telebot.TeleBot(BOT_TOKEN)
video = open('output.mp4', 'rb')


def generate_buttons(bts_names, markup):
    for button in bts_names:
        markup.add(types.KeyboardButton(button))
    return markup


markup = generate_buttons(['Product search', 'end bot'],
                          types.ReplyKeyboardMarkup(row_width=2))
# Define a function that will handle the /start command


@bot.message_handler(commands=['start'])
def send_hello(message):
    message = bot.reply_to(message, """Hi there! What you want to do?""",
                           reply_markup=markup)
    print(message.text)
    bot.register_next_step_handler(message, button)

# Define a function that will handle the button click


def echomessage(message):
    message = bot.reply_to(
        message, f"You said: {message.text}", reply_markup=markup)
    bot.register_next_step_handler(message, button)


def kill_bot(message):

    if message.text == 'yes':
        # Send a message confirming that the bot has been killed
        bot.reply_to(message, "Bot killed.")
        # Stop the bot
        bot.stop_polling()

    else:
        message = bot.reply_to(message, """Hi there! What you want to do?""",
                            reply_markup=markup)
        print(message.text)
        bot.register_next_step_handler(message, button)


def button(message):
    print(message.text)
    if message.text == 'Product search':
        item = bot.reply_to(message, "What product do you wnat to search for?")
        bot.register_next_step_handler(item, echomessage)

    elif message.text == 'end bot':
        bot.send_video(message.chat.id, open(
            'output.mp4', 'rb'), supports_streaming=True)

        message = bot.reply_to(message, """Hi there! What you want to do?""",
                               reply_markup=markup)
        bot.register_next_step_handler(message, kill_bot)

    else:

        message = bot.reply_to(message, """Please Click the buttons""",
                               reply_markup=markup)
        bot.register_next_step_handler(message, button)


# Start the bot

bot.polling()
