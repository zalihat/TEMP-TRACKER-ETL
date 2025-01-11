import requests
from dotenv import load_dotenv
import os
import pyarrow as pa
import pyarrow.parquet as pq 
import sys
import pandas as pd

# from util import create_or_update_directory\
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from datetime import datetime
def extract_weather_data():
    # create a directory data and sub directory raw to store the raw data. This will serve as the data lake for the project
    main_directory = "data_new"
    sub_directory = "raw"
    # Load the .env file
    load_dotenv()
    # Access the API key
    api_key = os.getenv("API_KEY")
    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    querystring = {"q":"8.950,7.0767"}
    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "weatherapi-com.p.rapidapi.com"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        data = response.json() 
        print(data)
       
    except Exception as e: 
        print("undexpected error: {e}")
    else:
        data = response.json() 
        json_df = pd.json_normalize(data)
        json_df['date'] = pd.to_datetime(json_df['location.localtime']).dt.date 
        
        raw_output_path = "data/raw"
        os.makedirs(raw_output_path, exist_ok=True)

        for unique_date in json_df['date'].unique():
            partition_path = os.path.join(raw_output_path, f"{unique_date}")
            os.makedirs(partition_path, exist_ok=True)
            data = json_df[json_df['date'] == unique_date]
            data.to_parquet(
                os.path.join(partition_path, f"{data['location.localtime'].iloc[0]}.parquet")
            ) 
        print("Raw data saved partitioned by date.")
extract_weather_data()

