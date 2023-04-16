import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
import datetime

# Replace YOUR_TOKEN with your Telegram bot token
TOKEN = '61240567 :AAHwSVOlFi333PdvhrFmV3Mai4lc0nGyaVY'
bot = telegram.Bot(token=TOKEN)

# Define the two buttons
button1 = InlineKeyboardButton('Get tomorrow\'s date', callback_data='date')

# Define the layout of the buttons
button_layout = [[button1]]

# Define the handler function for the /start command
def start(update, context):
    # Send a message with the button layout to the user
    reply_markup = InlineKeyboardMarkup(button_layout)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Welcome! Click the button to get tomorrow\'s date.', reply_markup=reply_markup)

# Define the handler function for button clicks
def button_click(update, context):
    query = update.callback_query
    if query.data == 'date':
        # Get tomorrow's date and send it back to the user
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        context.bot.send_message(chat_id=query.message.chat_id, text=f'Tomorrow\'s date is {tomorrow}.')

# Set up the bot with the handlers
updater = Updater(TOKEN, use_context=True)
updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CallbackQueryHandler(button_click))

# Start the bot
updater.start_polling()
updater.idle()
