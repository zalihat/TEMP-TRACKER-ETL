import requests
from dotenv import load_dotenv
import os
import pandas as pd
from datetime import datetime
from pathlib import Path
import os
import logging
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.functions import to_timestamp


# Configure logging
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

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
        #create a folder for the raw data in the shared volume
        raw_output_path = "/shared-data/raw"
        os.makedirs(raw_output_path, exist_ok=True)
        # Partition data by date and save as a parquet file in shared volume
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


def transform_weather_data():
    spark = SparkSession.builder \
    .appName("WeatherDataProcessing") \
   .config("spark.jars", "/shared-data/postgresql-42.7.5.jar") \
    .config("spark.driver.extraClassPath", "/shared-data/postgresql-42.7.5.jar") \
    .config("spark.executor.extraClassPath", "/shared-data/postgresql-42.7.5.jar") \
    .getOrCreate()
    
    folder_path = "/shared-data/raw"
    log_file = "processed_files.log"
  

    if os.path.exists(log_file):
        print(f"{folder_path} does exist")
        with open(log_file, "r") as f:
            processed_files = set(f.read().splitlines())
    else:
        processed_files = set()

    for root, _, files in os.walk(folder_path):
        print( f"this is the root{root}")
        print(f"this is the _ {_}")
        print(f"this is the file_path{files}")
        for file_name in files:
            if file_name.endswith(".parquet") and file_name not in processed_files:
                file_path = os.path.join(root, file_name)
                print(f"Processing: {file_path}")
                file_path = f"file://{file_path}"
                print(file_path)
                df = spark.read.parquet(file_path)
              
                df = df.toDF(*(c.replace(".", "_") for c in df.columns))  # Replace dots with underscores
        #         print(file_path)
                df.printSchema()
                processed_df = df.select(
                    col("location_name").alias("location"),
                    col("location_region").alias("region"),
                    col("location_country").alias("country"),
                    col("location_lat").alias("lat"),
                    col("location_lon").alias("lon"),
                    col("location_localtime").alias("localtime"),
                    col("current_temp_c").alias("temperature_c"),
                    col("current_temp_f").alias("temperature_f"),
                    col("current_feelslike_c").alias("feelslike_c"),
                    col("current_feelslike_f").alias("feelslike_f"),
                    col("date").alias("date")
                )
                processed_df = processed_df.withColumn("localtime", to_timestamp("localtime", "yyyy-MM-dd HH:mm"))

                print(processed_df.show())
                processed_files.add(file_name)
                
                with open(log_file, "a") as f:
                    f.write(file_name + "\n")
        #         processed_df.show()
                processed_df.write.jdbc(
                    url="jdbc:postgresql://postgres:5432/airflow",  # JDBC URL for Postgres
                    table="processed_weather_data",                # The table where data should be inserted
                    mode="append",                                 # Append mode for inserting data
                    properties={"user": "airflow", "password": "airflow", "driver": "org.postgresql.Driver"}
                )
            

    spark.stop()