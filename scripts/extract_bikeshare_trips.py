from datetime import datetime, timedelta
import os
import uuid
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from google.cloud import storage
from scripts import constants


def extract_bikeshare_trips(**kwargs):
    """
    This function ingest a bikeshare data from bigquery, transformed and then saved to GCS bucket
    using spark. It saves the data as parquet in GCS bucket. The data ingested is 1 day worth,
    and is the data of the previous day of the pipeline run date (given as parameter)
    
    Before saving, the corresponding partition of data is deleted (if exists). This is to ensure
    the data ingested in properly updated and the pipeline is idempotent.
    
    During the saving process by spark, the data is first saved into a temporary location 
    unique to this run. This is to make the pipeline robust and able to run multiple of this pipeline
    concurrently for different dates.
    
    kwargs["date_of_run"] (str): date when the pipelin is meant to run
    """
    date_of_run = datetime.strptime(kwargs["date_of_run"], "%Y-%m-%d").date()

    # Create Spark session with configurations from constants.py
    spark = (
        SparkSession.builder.appName(constants.APP_NAME)
        .master(constants.MASTER)
        .config("spark.sql.session.timeZone", constants.TIME_ZONE)
        .config("spark.jars", ",".join(constants.SPARK_JARS))
        .config("spark.hadoop.fs.gs.impl", constants.FS_IMPL)
        .config(
            "spark.hadoop.google.cloud.auth.service.account.enable",
            constants.AUTH_SERVICE_ACCOUNT_ENABLE,
        )
        .config("spark.hadoop.google.cloud.auth.type", constants.AUTH_TYPE)
        .getOrCreate()
    )

    # Set GCS credential
    spark._jsc.hadoopConfiguration().set(
        "google.cloud.auth.service.account.json.keyfile", constants.KEYFILE_PATH
    )

    # Ingest previous day data (offset by -1)
    prev_day = (date_of_run + timedelta(days=constants.DAY_OFFSET)).strftime("%Y-%m-%d")

    # Read data from BigQuery
    df = (
        spark.read.format("bigquery")
        .option("project", constants.SRC_PROJECT_ID)
        .option("dataset", constants.SRC_DATASET_ID)
        .option("table", constants.SRC_TABLE_ID)
        .load()
    )

    # filter for previous day data
    df = df.where(f"DATE(start_time) = '{prev_day}'")

    # Perform typecast
    df = (
        df.withColumn("trip_id", col("trip_id").cast("int"))
        .withColumn("bike_id", col("bike_id").cast("int"))
        .withColumn("end_station_id", col("end_station_id").cast("int"))
    )

    # Create partition columns
    df = df.withColumn(
        constants.PARTITION_COL_1, to_date(col("start_time"))
    ).withColumn(constants.PARTITION_COL_2, hour(col("start_time")))

    # Delete partition before backfilling to ensure idempotency
    storage_client = storage.Client()
    bucket = storage_client.get_bucket(constants.GCS_BUCKET_NAME)

    blobs = bucket.list_blobs(
        prefix=f"{constants.DATA_NAME}/{constants.PARTITION_COL_1}={prev_day}"
    )

    print(f"Deleting partition for {prev_day}")
    for blob in blobs:
        print("Deleting...")
        blob.delete()
    print(f"Completed deletion partition for {prev_day}")

    # Generate a unique suffix using the current timestamp or UUID
    temp_suffix = (
        f"temp_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_{str(uuid.uuid4())}"
    )
    temp_output_path = os.path.join(constants.TEMP_URI, temp_suffix)

    # Write to a temporary location in GCS to allow concurrent job runs without interference
    df.write.format("parquet").mode("append").partitionBy(
        constants.PARTITION_COL_1, constants.PARTITION_COL_2
    ).save(temp_output_path)

    # Copy each object to the final destination
    blobs = bucket.list_blobs(prefix=temp_suffix)
    for blob in blobs:
        bucket.rename_blob(
            blob,
            new_name=blob.name.replace(f"{temp_suffix}/", f"{constants.DATA_NAME}/"),
        )

    # Stop the Spark session
    spark.stop()


if __name__ == "__main__":
    extract_bikeshare_trips(date_of_run=constants.DEFAULT_RUN_DATE)
