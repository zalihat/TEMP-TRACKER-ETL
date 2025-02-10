import requests
from dotenv import load_dotenv
import os
import pyarrow as pa
import pyarrow.parquet as pq 
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path

def extract_weather_data():
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
        data = response.json() 
        json_df = pd.json_normalize(data)
        print(json_df.head())
        json_df['date'] = pd.to_datetime(json_df['location.localtime']).dt.date 
        
         
        # base_path = os.path.expanduser("~/shared-data")
        # home_dir = Path.home() 
        # base_path = home_dir / "shared-data"
        # raw_output_path = os.path.join(base_path, 'raw')
        raw_output_path = "/shared-data/raw"

        os.makedirs(raw_output_path, exist_ok=True)

        for unique_date in json_df['date'].unique():
            partition_path = os.path.join(raw_output_path, f"{unique_date}")
            os.makedirs(partition_path, exist_ok=True)
            data = json_df[json_df['date'] == unique_date]
            filename = f"{data['location.localtime'].iloc[0]}".replace(' ', '_').replace(':', '-')

            data.to_parquet(
                os.path.join(partition_path, f"{filename}.parquet")
            ) 
        print("Raw data saved partitioned by date.")
       
    except Exception as e: 
        print(f"undexpected error: {e}")
if __name__ == "__main__":
    extract_weather_data()

