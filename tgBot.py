import datetime as dt
import telebot
from telebot import types
from consolidated_function import *
import pandas as pd 
pd.options.mode.chained_assignment = None



BOT_TOKEN = "Your token"

# Create an instance of the Telegram bot
bot = telebot.TeleBot(BOT_TOKEN)
video = open('output.mp4', 'rb')
db_df = pd.read_csv('database2.csv')
db_df["full_product_name"] = db_df["Brand"] + " " + db_df["Product Name"]
unique_product_df = db_df.drop_duplicates(subset=['full_product_name', 'Product Code'])[["Category 1","Category 2","Category 3","Product Code","Brand","Product Name","full_product_name"]]
today = dt.date.today()-dt.timedelta(days=3)
db_df = db_df[db_df['avg_unit_price'].apply(lambda x: isinstance(x, float))]
db_df['avg_unit_price'] = db_df['avg_unit_price'].astype(float)
about = """
This code is for a Telegram bot that helps users make better purchasing decisions by providing insights into product pricing trends. The bot does this by analyzing historical price data of various products and offering recommendations based on price forecasts.

The bot offers three main features:

Product search & price prediction: Users can search for a specific product, and the bot will find the closest matches from a database of products. Upon selecting a product, the bot uses a special method to predict the product's price over the next week. Based on the prediction, it advises users whether to buy now or wait for a better price.

Data update: The bot regularly updates its product database to provide the most accurate and up-to-date information.

Bot termination: Users can choose to stop interacting with the bot, which will then send a goodbye video and end the session.)
"""
def generate_buttons(bts_names, markup):
    for button in bts_names:
        markup.add(types.KeyboardButton(button))
    return markup

markup = generate_buttons(["About",'Update','Product search', 'end bot'],
                          types.ReplyKeyboardMarkup(row_width=2))

# Define a function that will handle the /start command
@bot.message_handler(commands=['start'])
def send_hello(message):
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
    if message.text == 'None of the above':
        message = bot.reply_to(message, f'Sorry, I will send you back to home page', reply_markup=markup)
        home(message)
    else:
        one_year_ago = today - dt.timedelta(days=365)
        now = str(today.strftime('%Y%m%d'))
        one_year = str(one_year_ago.strftime('%Y%m%d'))
        result = forecast_price(message.text, db_df,int(now),int(one_year))
        graph(message.text, db_df,int(now),int(one_year))
        bot.send_photo(message.chat.id, photo=open('sample_plot.png', 'rb'))
        message = bot.reply_to(message, f'{result}', reply_markup=markup)
        bot.register_next_step_handler(message, button)

def kill_bot(message):

    if message.text == 'yes':
        # Send a message confirming that the bot has been killed
        bot.reply_to(message, "Bot killed.")
        # Stop the bot
        bot.stop_polling()

    else:
        home(message)


def button(message,df=db_df):
    global db_df
    try:
        if message.text == 'Product search':
            item = bot.reply_to(message, "What product do you want to search for?")
            bot.register_next_step_handler(item, search_product)
        
        elif message.text == 'Update':
            bot.reply_to(message, "Updating database, Please wait...")
            date = str(today.strftime('%Y%m%d'))
            db = initiate_update_db(df,int(20230412))
            #drop the rows with average price is not float
            db = db[db['avg_unit_price'].apply(lambda x: isinstance(x, float))]
            db['avg_unit_price']  = db['avg_unit_price'].astype(float)
            db['timestamp'] = db['timestamp'].astype(float)
            #update the global database
            db_df = db

            message = bot.reply_to(message, 'Successful Updated', reply_markup=markup)
            home(message)


        elif message.text == 'end bot':
            bot.send_video(message.chat.id, open(
                'output.mp4', 'rb'), supports_streaming=True)

            message = bot.reply_to(message, """Hi there! What you want to do?""",
                            reply_markup=markup)
        
            bot.register_next_step_handler(message, kill_bot)

        elif message.text == 'About':
                bot.reply_to(message,f"{about}")
                home(message)


        else:

            message = bot.reply_to(message, """Please Click the buttons""",
                                reply_markup=markup)
            bot.register_next_step_handler(message, button)
    except:
            message = bot.reply_to(message, """Please Click the buttons""",
                                reply_markup=markup)
            bot.register_next_step_handler(message, button) 

# Start the bot

bot.polling()
