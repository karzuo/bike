from pyspark.sql import SparkSession
from pyspark.sql.functions import *


# Create a Spark session
spark = SparkSession.builder \
    .appName("BikeShareEtl") \
    .master("local[*]")  \
    .config('spark.jars', 'jars/spark-3.5-bigquery-0.42.0.jar,jars/gcs-connector-3.0.4-shaded.jar') \
    .config("spark.hadoop.fs.gs.impl", 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem') \
    .config("spark.hadoop.google.cloud.auth.service.account.enable", 'true') \
    .config("spark.hadoop.google.cloud.auth.type", 'SERVICE_ACCOUNT_JSON_KEYFILE') \
    .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", 'scripts/service_account.json') \
    .getOrCreate()

# # Bigquery table
# project_id = "bigquery-public-data"
# dataset_id = "austin_bikeshare"
# table_id = "bikeshare_trips" 

# Read data from BigQuery
# df = spark.read \
#     .format("bigquery") \
#     .option("project", project_id) \
#     .option("dataset", dataset_id) \
#     .option("table", table_id) \
#     .load()

# # BigQuery SQL query to fetch data for the previous day
# query = f"""
# SELECT *
# FROM `bigquery-public-data.austin_bikeshare.bikeshare_trips`
# WHERE DATE(start_time) = '{previous_day}'
# """

# # Read data from BigQuery using the SQL query
# df = spark.read.format('bigquery') \
#     .option('query', query) \
#     .load()

# Test the setup
data = [("Alice", "2024-02-27 10:30:45.123"), ("Bob", "2024-02-27 16:30:45.123"), ("Charlie", "2024-02-28 17:30:45.123")]
df = spark.createDataFrame(data, ["Name", "start_time"])
    
# # Filter for previous day
# df = df.filter("DATE(start_time)='2024-06-20'")

# Create partition columns
df = df.withColumn('partition_date', to_date(col("start_time")))
df = df.withColumn('partition_hour', hour(col("start_time")))

# # Sort by time
# df = df.orderBy("start_time", ascending=True)

# Write to GCS
# df.show()
# df.write.parquet(
#     'testpq',
#     mode="overwrite",
#     partitionBy=['partition_date', 'partition_hour']
# )
# df.write \
#     .format("parquet") \
#     .mode("overwrite") \
#     .partitionBy("partition_date", "partition_hour") \
#     .save("gs://bike-share-hw/testpq")

spark.read.parquet('gs://bike-share-hw/testpq').show()
# Stop the Spark session
spark.stop()