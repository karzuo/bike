# ETL Settings
DAY_OFFSET = -1  # number of days to offset from given
PARTITION_COL_1 = "partition_date"  # name of first partition column (date)
PARTITION_COL_2 = "partition_hour"  # name of second partition column (hour)
DEFAULT_RUN_DATE = "2024-04-30"  # default date to run if not given (for testing)

# Source Data Details
SRC_PROJECT_ID = "bigquery-public-data"  # gcp project id of source data
SRC_DATASET_ID = "austin_bikeshare"  # bigquery dataset id of source data
SRC_TABLE_ID = "bikeshare_trips"  # bigquery table id of source data

# Metadata of ingested data in GCS
GCS_BUCKET_NAME = "bike-share-hw"  # gcs bucket to ingest data into
DATA_NAME = "bikeshare"  # name of dataset ingested into gcs
SOURCE_URI_PREFIX = f"gs://{GCS_BUCKET_NAME}/{DATA_NAME}/"  # path of dataset in gcs
SOURCE_URI = f"gs://{GCS_BUCKET_NAME}/{DATA_NAME}/*"  # uri of dataset in gcs
SOURCE_DATA_FORMAT = "PARQUET"  # datatype ingested into gcs
PARTITION_MODE = "AUTO"  # parameter for bigquery external table creation from parquet

# Bigquery external table config
BQ_PROJECT_ID = "bike-451619"  # project id data
BQ_DATASET_ID = "tech_homework"  # dataset id of bigquery for external table
BQ_TABLE_ID = "bikeshare"  # name of external table in bigquery
BQ_TABLE_REF = (
    f"{BQ_PROJECT_ID}.{BQ_DATASET_ID}.{BQ_TABLE_ID}"  # full reference to external table
)

# Spark configs
APP_NAME = "BikeShareEtl"
MASTER = "local[*]"
TIME_ZONE = "UTC"
SPARK_JARS = [
    "jars/spark-3.5-bigquery-0.42.0.jar",
    "jars/gcs-connector-3.0.4-shaded.jar",
]  # NOTE: if modified, to update corresponding JARS download URLs in Dockerfile
FS_IMPL = "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem"
AUTH_SERVICE_ACCOUNT_ENABLE = "TRUE"
AUTH_TYPE = "SERVICE_ACCOUNT_JSON_KEYFILE"
KEYFILE_PATH = "scripts/service_account.json"
# Note: if KEYFILE_PATH modified, to update GOOGLE_APPLICATION_CREDENTIALS in Dockerfile
