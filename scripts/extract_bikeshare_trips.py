from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
from google.cloud import storage
import constants


def extract_bikeshare_trips(**kwargs):
    date_of_run=datetime.strptime(kwargs['date_of_run'], '%Y-%m-%d').date()

    # Create a Spark session
    spark = SparkSession.builder \
        .appName("BikeShareEtl") \
        .master("local[*]")  \
        .config("spark.sql.session.timeZone", "UTC") \
        .config('spark.jars', 'jars/spark-3.5-bigquery-0.42.0.jar,jars/gcs-connector-3.0.4-shaded.jar') \
        .config("spark.hadoop.fs.gs.impl", 'com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem') \
        .config("spark.hadoop.google.cloud.auth.service.account.enable", 'true') \
        .config("spark.hadoop.google.cloud.auth.type", 'SERVICE_ACCOUNT_JSON_KEYFILE') \
        .getOrCreate()
        
    # Set GCS credential
    spark._jsc.hadoopConfiguration().set("google.cloud.auth.service.account.json.keyfile", 'scripts/service_account.json')

    # Data details
    project_id='bigquery-public-data'
    dataset_id='austin_bikeshare'
    table_id='bikeshare_trips'
    prev_day = (date_of_run + timedelta(days=constants.DAY_OFFSET)).strftime('%Y-%m-%d')

    # Read data from BigQuery
    df = spark.read \
        .format("bigquery") \
        .option("project", project_id) \
        .option("dataset", dataset_id) \
        .option("table", table_id) \
        .load()
        
    df = df.where(f"DATE(start_time) = '{prev_day}'")
    
    # Perform typecast
    df= df.withColumn('trip_id', col("trip_id").cast("int")) \
          .withColumn('bike_id', col("bike_id").cast("int")) \
          .withColumn('end_station_id', col("end_station_id").cast("int"))

    # Create partition columns
    df = df.withColumn('partition_date', to_date(col("start_time"))) \
           .withColumn('partition_hour', hour(col("start_time")))

    # Delete partition before backfilling to ensure idempotency
    storage_client = storage.Client()
    bucket = storage_client.get_bucket('bike-share-hw')

    blobs = bucket.list_blobs(prefix=f'bikeshare/partition_date={prev_day}')

    print(f"Deleting partition for {prev_day}")
    for blob in blobs:
        print("Deleting...")
        blob.delete()
    print(f"Completed deletion partition for {prev_day}")

    # Write to GCS
    # TODO make bucket configurable
    df.write \
        .format("parquet") \
        .mode("append") \
        .partitionBy("partition_date", "partition_hour") \
        .save("gs://bike-share-hw/bikeshare")

    # Stop the Spark session
    spark.stop()
    
# TODO remove hardcode
if __name__ == "__main__":
    extract_bikeshare_trips(date_of_run='2024-06-20')