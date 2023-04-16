import threading
import telebot
from telebot import types

BOT_TOKEN = '6120420567:AAHwSVOlFi333PdvhrFmV3Mai4lc0nGyaVY'

# Create an instance of the Telegram bot
bot = telebot.TeleBot(BOT_TOKEN)

# Define a function that will handle the /start command
@bot.message_handler(commands=['start'])
def start(message):
    # Create a keyboard with two buttons
    keyboard = types.InlineKeyboardMarkup()
    date_button = types.InlineKeyboardButton("Tomorrow's Date", callback_data='date')
    kill_button = types.InlineKeyboardButton("Kill the Bot", callback_data='kill')
    keyboard.row(date_button, kill_button)

    # Send a message with the buttons to the user
    bot.send_message(message.chat.id, 'Choose an option:', reply_markup=keyboard)

# Define a function that will handle the button click
@bot.callback_query_handler(func=lambda call: True)
def button(call):
    if call.data == 'date':
        # Get tomorrow's date
        msg = bot.send_message(call.message.chat.id, "What product do you wnat to search for?")

        # Define a function that will handle the user's input
        @bot.message_handler(func=lambda message: True)
        def echo_message(message):
            # Check if the message is a response to a prompt
            chat_id = message.chat.id
            if chat_id in prompts:
                # Send the user's input back to them
                bot.send_message(chat_id, f"You said: {message.text}")

                # Remove the prompt message from the chat
                bot.delete_message(chat_id, prompts[chat_id].message_id)

                # Remove the echo_message function from the handlers
                bot.remove_message_handler(echo_message)

                # Remove the prompt message from the prompts dictionary
                del prompts[chat_id]

        # Add the echo_message function to the message handlers
        bot.add_message_handler(echo_message)

        # Set a timeout to remove the echo_message function after 30 seconds
        threading.Timer(30.0, bot.remove_message_handler, args=(echo_message,)).start()

    elif call.data == 'kill':
        # Send a message confirming that the bot will be killed
        bot.send_message(call.message.chat.id, "Are you sure you want to kill the bot? Type 'yes' to confirm.")

        # Wait for the user's response
        @bot.message_handler(func=lambda message: message.text.lower() == 'yes')
        def kill_bot(message):
            # Send a message confirming that the bot has been killed
            bot.send_message(call.message.chat.id, "Bot killed.")

            # Stop the bot
            bot.stop_polling()

# Start the bot
prompts = {}
bot.polling()
