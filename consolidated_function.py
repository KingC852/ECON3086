import pandas as pd
from fuzzywuzzy import process
import re
import requests
import io
from tqdm import tqdm
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt

# this function is used to call the available price watch json name from the api
def call_price_watch_list_api(start_date, end_date):
    url = "https://api.data.gov.hk/v1/historical-archive/list-file-versions"
    params = {
        "url": "https://online-price-watch.consumer.org.hk/opw/opendata/pricewatch_en.csv",
        "start": start_date,
        "end": end_date
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        timestamps = data["timestamps"]
        return timestamps
    else:
        return("Error: API request failed")
    
# this function is used to call the price watch api, this will return the json file as a dataframe
def price_watch_api(api_link, params):
    response = requests.get(api_link, params=params)

    if response.status_code == 200:
        data = response.text.strip()
        temp_df = pd.read_csv(io.StringIO(data))
        temp_df.rename({"ï»¿Category 1":"Category 1"}, axis=1, inplace = True)
        temp_df["timestamp"] = params["time"].split("-")[0]
        return {"msg":"200", "data":temp_df}  

    else:
        return {"msg":"err", "data":params["time"]}
    
# this function is used to consolidate the call_price_watch_list_api and price_watch_api function and execute them at once
# this function will return a dataframe where the dataframe has been cleaned and processed
def executing_price_watch_api(start_date, end_date):
    # runnign the price watch list api
    timestamps = call_price_watch_list_api(start_date, end_date)

    # running the price watch api
    params_list = []
    for timestamp in timestamps:
        params_list.append({"url": "https://online-price-watch.consumer.org.hk/opw/opendata/pricewatch_en.csv","time": timestamp})
    api_link = "https://api.data.gov.hk/v1/historical-archive/get-file"

    err_list = []

    result_df = pd.DataFrame()
    for params in tqdm(params_list):
        result = price_watch_api(api_link, params) 
        if result["msg"] == "200":
            df = result["data"]
            df = offer(df)
            df["full_product_name"] = df["Brand"] + " " + df["Product Name"]
            df["preprocessed_product_names"] = df["full_product_name"].apply(preprocess_string)
            result_df = pd.concat([result_df, df])
        else:
            print(f"Error: API request failed for {result['data']}")
            err_list.append(result["data"])
    return result_df.reset_index(drop=True)

def offer(raw):
    for ind in raw[raw['Offers'].isna()==False].index.to_list():
        try:
            # print(ind)
            i = raw.loc[ind,'Offers']
            if 'to save ' in i and len(i) < 20:
                deal = i.lower().replace('buy ', '').split(' to save $')
                # print(deal)
                raw.loc[ind,'min_unit']=int(deal[0])
                raw.loc[ind,'avg_unit_price']=(float(raw.loc[ind,'Price'])*int(deal[0])-float(deal[1]))/int(deal[0])
            elif 'free' in i and len(i) < 20:
                for word in ['Buy ', ' free']:
                    i = i.replace(word, '')
                deal = i.split(' get ')
                # print(deal)
                raw.loc[ind,'min_unit']=int(deal[0])+int(deal[1])
                raw.loc[ind,'avg_unit_price']=(float(raw.loc[ind,'Price'])*int(deal[0]))/raw.loc[ind,'min_unit']
            elif 'at' in i and len(i) < 20:
                deal = i.lower().replace('buy ', '').split(' at $')
                raw.loc[ind,'avg_unit_price']=float(deal[1])/int(deal[0])
            elif 'for' in i and len(i) < 20: 
                deal = i.split(' for $')
                raw.loc[ind,'min_unit']=int(deal[0])
                raw.loc[ind,'avg_unit_price']=float(deal[1])/int(deal[0])
            else:
                # print('error', i)
                raw.loc[ind,'min_unit'] = 0
                raw.loc[ind,'avg_unit_price'] = raw.loc[ind,'Price']
        except:
            raw.loc[ind,'min_unit'] = 0
            raw.loc[ind,'avg_unit_price'] = raw.loc[ind,'Price']
    raw['avg_unit_price'] = raw['avg_unit_price'].fillna(raw['Price'])
    return raw

def preprocess_string(s):
    # Remove or replace any non-alphanumeric characters, including punctuation marks and spaces
    return re.sub(r"[^\w\s]", "", s).lower()

def find_top_matches(user_input, unique_product_df, column_name='full_product_name', top_n=3):
    preprocessed_user_input = preprocess_string(user_input)
    unique_product_df["preprocessed_product_names"] = unique_product_df[column_name].apply(preprocess_string)

    temp_match_list = process.extract(preprocessed_user_input, unique_product_df["preprocessed_product_names"], limit=top_n)

    result_df = pd.DataFrame()
    sim_score = []
    for match in temp_match_list:
        matched_row = unique_product_df[unique_product_df["preprocessed_product_names"] == match[0]]
        sim_score.append(match[1])
        result_df = pd.concat([result_df, matched_row])
    result_df['similarity_score'] = sim_score
    return result_df.reset_index(drop=True)

# kick start the scraping and appending function
def initiate_update_db(db_df, update_date):
    latest_date = db_df["timestamp"].max()

    updated_df = executing_price_watch_api(latest_date, update_date)
    db_df = pd.concat([db_df, updated_df])
    db_df = db_df.reset_index(drop=True)

    return db_df

# startdate, enddate, product_name 
# query the product with a certain date range
def product_query(db_df, startdate, enddate, product_name):
    return db_df[(db_df['timestamp'].astype('int32') <= int(enddate)) & (db_df['timestamp'].astype('int32') >= int(startdate) )& (db_df['full_product_name'] == product_name)]
    
def forecast_price(product_name, data,now,one_year):
    """
    This function takes a product code and a file path for a CSV file containing time-series data for multiple products.
    It fits an ARIMA model to the time-series data for the specified product, makes a forecast for the next 7 days, 
    and then determines whether to buy or wait based on the forecast.
    
    Parameters:
    - product_code (str): the code for the product of interest
    - data_file_path (str): the file path for the CSV file containing the time-series data
    
    Returns:
    - A string indicating whether to buy or wait based on the forecasted prices
    """
    
    # Read in the data

    # Subset the data for the product you're interested in
    product_data = data[(data["full_product_name"] == product_name)&(data['timestamp']<=now)&(data['timestamp']>=one_year)]
    # Convert the date column to a datetime index
    product_data['timestamp'] = pd.to_datetime(data['timestamp'], format='%Y%m%d')
    product_data.set_index('timestamp', inplace=True)

    # Fit an ARIMA model to the data
    model = ARIMA(product_data['avg_unit_price'].astype(float), order=(1, 1, 1))
    fit = model.fit()

    # Make a forecast for the next 7 days
    forecast = fit.forecast(steps=7)

    # Get the last observed price
    last_price = float(product_data['avg_unit_price'].iloc[-1])

    # Get the forecasted prices
    forecast_prices = forecast.values

    # Determine whether to buy or not based on the forecast
    if all(forecast_prices < last_price):
        return 'The price is forecasted to decrease. You should wait to buy.'
    else:
        return 'The price is forecasted to increase or stay the same. You should buy now.'
    

def graph(product_name,data,now,one_year):
# Read in the data
    # Convert the date column to datetime
    data = data[(data["full_product_name"] == product_name)&(data['timestamp']<=now)&(data['timestamp']>=one_year)]
    data['timestamp'] = pd.to_datetime(data['timestamp'], format='%Y%m%d')
    # Group the data by date and calculate the mean price
    mean_prices = data.groupby('timestamp')['avg_unit_price'].mean()
    # Create a line plot of the mean price over time
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(mean_prices.index, mean_prices.values)
    #add a docted line with the mean price of the whole dataset
    ax.axhline(mean_prices.mean(), color='red', linestyle='--')
    # Set the plot title and axis labels
    ax.set_title('Overall Price Trend of Product')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price')
    fig.savefig('sample_plot.png')
    
