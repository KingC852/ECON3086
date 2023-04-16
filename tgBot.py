import datetime
import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext


# Telegram Bot Token
TOKEN = '6120420567:AAHwSVOlFi333PdvhrFmV3Mai4lc0nGyaVY'

# Create an instance of the Telegram bot
bot = telegram.Bot(TOKEN)

# Define a function that will handle the /start command
def start(update, context):
    # Create a keyboard with a single button
    keyboard = [[InlineKeyboardButton("Tomorrow's Date", callback_data='date')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send a message with the button to the user
    update.message.reply_text('Click the button to get tomorrow\'s date:', reply_markup=reply_markup)

# Define a function that will handle the button click
def button(update, context):
    query = update.callback_query

    # Get tomorrow's date
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)

    # Send the date to the user
    query.answer(text=f"Tomorrow's date is {tomorrow.strftime('%m/%d/%Y')}")

# Create an instance of the Updater class and add the handlers
updater = Updater(TOKEN)
updater.dispatcher.add_handler(CommandHandler('start', start, context=CallbackContext()))
updater.dispatcher.add_handler(CallbackQueryHandler(button, context=CallbackContext()))

# Start the bot
updater.start_polling()
updater.idle()
