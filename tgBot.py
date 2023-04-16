import datetime as dt
import telebot
from telebot import types
from consolidated_function import *
import pandas as pd 


BOT_TOKEN = '6120420567:AAHwSVOlFi333PdvhrFmV3Mai4lc0nGyaVY'

# Create an instance of the Telegram bot
bot = telebot.TeleBot(BOT_TOKEN)
video = open('output.mp4', 'rb')
db_df = pd.read_csv('price_watch_20210405-20230405.csv')
db_df["full_product_name"] = db_df["Brand"] + " " + db_df["Product Name"]
unique_product_df = db_df.drop_duplicates(subset=['full_product_name', 'Product Code'])[["Category 1","Category 2","Category 3","Product Code","Brand","Product Name","full_product_name"]]
today = dt.date.today()

def generate_buttons(bts_names, markup):
    for button in bts_names:
        markup.add(types.KeyboardButton(button))
    return markup

markup = generate_buttons(['Update','Product search', 'end bot'],
                          types.ReplyKeyboardMarkup(row_width=2))
# Define a function that will handle the /start command


@bot.message_handler(commands=['start'])
def send_hello(message):
    # print(db_df)
    message = bot.reply_to(message, """Hi there! What you want to do?""",
                           reply_markup=markup)
    
    bot.register_next_step_handler(message, button)

# Define a function that will handle the button click
def home(message):
    message = bot.reply_to(message, """Hi there! What you want to do?""",
    reply_markup=markup)

    bot.register_next_step_handler(message, button)

def search_product(message):
    user_input = message.text
    matches = find_top_matches(user_input, unique_product_df)
    bts_names = matches["full_product_name"].tolist()
    bts_names.append('None of the above')
    products = generate_buttons(bts_names, types.ReplyKeyboardMarkup(row_width=2))
    message = bot.reply_to(message, f'Which product do you want?', reply_markup=products)
    bot.register_next_step_handler(message, preddict_price)

def preddict_price(message):
    # print(db_df)
    # print(message.text)
    if message.text == 'None of the above':
        message = bot.reply_to(message, f'Sorry, I will send you back to home page', reply_markup=markup)
        home(message)
    else:
        # print(db_df)
        one_year_ago = today - dt.timedelta(days=365)
        product_df = product_query(db_df, str(today.strftime('%Y%m%d')),str(one_year_ago.strftime('%Y%m%d')), message.text)
        print(product_df)
        message = bot.reply_to(message, f'Predicted price is 1000', reply_markup=markup)
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
        
        bot.register_next_step_handler(message, button)


def button(message,db_df=db_df):
    
    if message.text == 'Product search':
        item = bot.reply_to(message, "What product do you wnat to search for?")
        bot.register_next_step_handler(item, search_product)
    
    elif message.text == 'Update':

        # date = str(today.strftime('%Y%m%d'))
        # print(db_df.columns.values)
        db_df = initiate_update_db(db_df,int(20230412))
        # print(db_df_update['timestamp'].tail(10))
        message = bot.reply_to(message, 'Updated', reply_markup=markup)
        message = bot.reply_to(message, """Hi there! What you want to do?""",
        reply_markup=markup)
        bot.register_next_step_handler(message, button)


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
