from pyspark.sql import SparkSession

# Initialize Spark session
spark = SparkSession.builder.appName("Spark Test App").master("spark://spark:7077").getOrCreate() 
# Pointing to the Spark master service in Docker Compose.

# Create a sample DataFrame
data = [("Alice", 1), ("Bob", 2), ("Charlie", 3)]
columns = ["Name", "Value"]
df = spark.createDataFrame(data, columns)

# Show the DataFrame
df.show()

# Perform a simple transformation
df_transformed = df.withColumn("Value_plus_1", df["Value"] + 1)

# Show the transformed DataFrame
df_transformed.show()

# Stop the Spark session
spark.stop()
