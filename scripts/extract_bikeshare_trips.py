from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from google.cloud import storage
from scripts import constants


def extract_bikeshare_trips(**kwargs):
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

    # Write to GCS
    df.write.format("parquet").mode("append").partitionBy(
        constants.PARTITION_COL_1, constants.PARTITION_COL_2
    ).save(constants.SOURCE_URI_PREFIX)

    # Stop the Spark session
    spark.stop()


if __name__ == "__main__":
    extract_bikeshare_trips(date_of_run=constants.DEFAULT_RUN_DATE)
