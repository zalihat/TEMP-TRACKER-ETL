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

def transform_weather_data():
    # spark = SparkSession.builder.appName("WeatherDataProcessing").getOrCreate()
    spark = SparkSession.builder \
    .appName("WeatherDataProcessing") \
   .config("spark.jars", "/shared-data/postgresql-42.7.5.jar") \
    .config("spark.driver.extraClassPath", "/shared-data/postgresql-42.7.5.jar") \
    .config("spark.executor.extraClassPath", "/shared-data/postgresql-42.7.5.jar") \
    .getOrCreate()
    
    folder_path = "/shared-data/raw"
    processed_output_path = "/shared-data/processed"
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
            # and file_name not in processed_files:
                file_path = os.path.join(root, file_name)
                print(f"Processing: {file_path}")
                
        #         # try:
        #         print('reading files')
        #         print(f"file_path")
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
                
        #         unique_dates = [row.date for row in processed_df.select("date").distinct().collect()]
        #         for unique_date in unique_dates:
        #             partition_path = os.path.join(processed_output_path, f"{unique_date}")
        #             os.makedirs(partition_path, exist_ok=True)
        #             data = processed_df.filter(col("date") == unique_date)
        #             data.write.mode("overwrite").parquet(os.path.join(partition_path, f"{unique_date}.parquet"))
                
        #         print("Processed data saved partitioned by date.")
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
                # records = [row.asDict() for row in processed_df.collect()]
                
                # return records
            
                # except Exception as e:
                #     logging.error(f"Error processing file {file_name}: {e}")
                #     print(f"An error occurred processing {file_name}. Check logs for details.")

    spark.stop()

if __name__ == "__main__":
    transform_weather_data()
