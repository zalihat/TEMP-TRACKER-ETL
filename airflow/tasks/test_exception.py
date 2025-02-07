import os
import logging
# from pyspark.sql import SparkSession
# from pyspark.sql.functions import col

# Configure logging
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def transform_weather_data():
    # spark = SparkSession.builder.appName("WeatherDataProcessing").getOrCreate()
    
    folder_path = "data/raw"
    processed_output_path = "/opt/airflow/data/processed"
    log_file = "processed_files.log"
  

    file_path = "data/raw/2025-02-05/2025-02-05.parquet"

    if os.path.exists(file_path):
        print(f"✅ File exists: {file_path}")
    else:
        print(f"❌ File not found: {file_path}")

    print("Files in directory:", os.listdir("data/raw/2025-02-05/"))

    if os.path.exists(log_file):
        print(f"{folder_path} does exist")
        with open(log_file, "r") as f:
            processed_files = set(f.read().splitlines())
    else:
        processed_files = set()

    for root, _, files in os.walk(folder_path):
        for file_name in files:
            if file_name.endswith(".parquet") and file_name not in processed_files:
                file_path = os.path.join(root, file_name)
                print(f"Processing: {file_path}")
                
    #             # try:
    #             print('reading files')
    #             print(f"file_path")
    #             df = spark.read.parquet(file_path)
    #             processed_df = df.select(
    #                 col("location.name").alias("location"),
    #                 col("location.region").alias("region"),
    #                 col("location.country").alias("country"),
    #                 col("location.lat").alias("lat"),
    #                 col("location.lon").alias("lon"),
    #                 col("location.localtime").alias("localtime"),
    #                 col("current.temp_c").alias("temperature_c"),
    #                 col("current.temp_f").alias("temperature_f"),
    #                 col("current.feelslike_c").alias("feelslike_c"),
    #                 col("current.feelslike_f").alias("feelslike_f"),
    #                 col("date").alias("date")
    #             )
                
    #             unique_dates = [row.date for row in processed_df.select("date").distinct().collect()]
    #             for unique_date in unique_dates:
    #                 partition_path = os.path.join(processed_output_path, f"{unique_date}")
    #                 os.makedirs(partition_path, exist_ok=True)
    #                 data = processed_df.filter(col("date") == unique_date)
    #                 data.write.mode("overwrite").parquet(os.path.join(partition_path, f"{unique_date}.parquet"))
                
    #             print("Processed data saved partitioned by date.")
    #             processed_files.add(file_name)
                
    #             with open(log_file, "a") as f:
    #                 f.write(file_name + "\n")
    #             processed_df.show()
    #             records = [row.asDict() for row in processed_df.collect()]
    #             return records
            
                # except Exception as e:
                #     logging.error(f"Error processing file {file_name}: {e}")
                #     print(f"An error occurred processing {file_name}. Check logs for details.")

    # spark.stop()

if __name__ == "__main__":
    transform_weather_data()
