<h1>Telegram Price Bot</h1>

Telegram Price Bot is a Python-based Telegram bot that provides users with insights into product pricing trends. The bot analyzes historical price data of various products and offers recommendations based on price forecasts. It offers three main features:

    Product search & price prediction: Users can search for a specific product, and the bot will find the closest matches from a database of products. Upon selecting a product, the bot uses a special method to predict the product's price over the next week. Based on the prediction, it advises users whether to buy now or wait for a better price.

    Data update: The bot regularly updates its product database to provide the most accurate and up-to-date information. Users can trigger a manual update using the "Update" button.

    Bot termination: Users can choose to stop interacting with the bot, which will then send a goodbye video and end the session.

Prerequisites

Before running the Telegram Price Bot, make sure you have the following dependencies installed:

    Python 3.10 or higher
    pandas
    telebot
    matplotlib
    fuzzywuzzy
    re
    requests
    io
    tqdm
    statsmodels

You can install these dependencies using pip, the Python package manager, by running the following command:

    pip install pandas telebot matplotlib fuzzywuzzy re requests io tqdm statsmodels

Usage

    Clone this repository to your local machine.
    Update the BOT_TOKEN variable in the tgBot.py file with your own Telegram bot token.
    Place your product database CSV file in the same directory as the tgBot.py file, and update the db_df variable in the tgBot.py file to load your database.
    Run the tgBot.py file to start the Telegram bot.
    Start a chat with your Telegram bot and send the /start command to initiate the conversation.
    Follow the bot's instructions to interact with it using the available commands and buttons.

The main functionalities of the consolidated function are as follows:

    call_price_watch_list_api(start_date, end_date): This function is used to call the available price watch JSON names from the API. It takes the start date and end date as input and returns a list of timestamps.

    price_watch_api(api_link, params): This function is used to call the Price Watch API and returns the JSON data as a Pandas DataFrame. It takes the API link and parameters as input and returns a dictionary containing the response message and the DataFrame.

    executing_price_watch_api(start_date, end_date): This function consolidates the above two functions and executes them at once. It takes the start date and end date as input and returns a cleaned and processed DataFrame.

    offer(raw): This function processes the "Offers" column of the DataFrame returned by the Price Watch API and calculates the minimum unit and average unit price for each product.

    preprocess_string(s): This function preprocesses a string by removing or replacing any non-alphanumeric characters, including punctuation marks and spaces. It is used for string matching purposes.

    find_top_matches(user_input, unique_product_df, column_name='full_product_name', top_n=3): This function finds the top N matches of a user input string in a DataFrame of unique product names. It uses fuzzy string matching to find the matches based on similarity scores.

    fit_arima_model(product_df, product_name): This function fits an ARIMA model to the time series data of a product's prices and returns the model summary and forecasted prices.

    plot_product_price(product_df, product_name, start_date, end_date): This function plots the historical price data of a product from the Price Watch API.

    plot_forecasted_price(product_df, product_name, start_date, end_date, forecast_start_date, forecast_end_date): This function plots the historical price data and the forecasted prices of a product.

Commands and Buttons for the telegram bot

    /start: Start the conversation with the bot.
    Product search: Search for a specific product and get price predictions.
    Update: Manually update the product database.
    end bot: End the bot session.
    About: Learn more about the bot.
