import os
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    filename="error.log",  # Log file name
    level=logging.ERROR,   # Log only errors and above
    format="%(asctime)s - %(levelname)s - %(message)s"
)
def transform_weather_data():
    folder_path = "data/raw"
    processed_output_path = "data/processed"
    # Path to the log file for tracking processed files
    log_file = "logs/processed_files.log"

    # Load the list of already processed files
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            processed_files = set(f.read().splitlines())
    else:
        processed_files = set()
    
        # Loop through the folder
    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".parquet"):
                file_path = os.path.join(root, file_name)
                # Check if the file has already been processed
                if file_name not in processed_files:
                    print(f"Processing: {file_name}")
                    
                    try:   # Read and process the Parquet file
                        df = pd.read_parquet(file_path)
                        processed_df = pd.DataFrame()
                        processed_df['location'] = df['location.name'] 
                        processed_df['region'] = df['location.region'] 
                        processed_df['country'] = df['location.country']
                        processed_df['lat'] = df['location.lat']
                        processed_df['lon'] = df['location.lon']
                        processed_df['localtime'] = df['location.localtime']
                        processed_df['temperature_c'] = df['current.temp_c']
                        processed_df['temperature_f'] = df['current.temp_f']
                        processed_df['feelslike_c'] = df['current.feelslike_c']
                        processed_df['feelslike_f'] = df['current.feelslike_f']
                        processed_df['date'] = df['date']

                        # processed_output_path = 
                        for unique_date in processed_df['date'].unique():
                            partition_path = os.path.join(processed_output_path, f"{unique_date}")
                            os.makedirs(partition_path, exist_ok=True)
                            data = processed_df[processed_df['date'] == unique_date]
                            data.to_parquet(
                                os.path.join(partition_path, f"{data['localtime'].iloc[0]}.parquet")
                            ) 
                        print("processed data saved partitioned by date.")
                        # Mark the file as processed
                        processed_files.add(file_name)
                        # Append the processed file to the log
                        with open(log_file, "a") as f:
                            f.write(file_name + "\n")
                        print(processed_df.head())   
                    
                        return processed_df 
                    # except:
                    except FileNotFoundError as e:
                        logging.error(f"File not found: {e}")
                        print("The file was not found. Please check the file path.")
                    except pd.errors.EmptyDataError:
                        logging.error("Attempted to read an empty file.")
                        print("The file is empty. Please provide a valid file.")
                    except pd.errors.ParserError:
                        logging.error("File parsing error occurred.")
                        print("Error parsing the file. Check if it's formatted correctly.")
                    except Exception as e:
                        logging.error(f"An unexpected error occurred: {e}")
                        print("An unexpected error occurred. Please check the logs.")
            else:
                print(f"Skipping already processed file: {file_name}")
                    


            


# transform_weather_data()

