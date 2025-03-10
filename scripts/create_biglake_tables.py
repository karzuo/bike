from google.cloud import bigquery
from google.cloud.exceptions import Conflict

from scripts import constants


def create_biglake_table():
    """This function creates a bigquery external table to reference the data
    stored in GCS. It first delete the table (if exists) then re-create it.
    
    The concurrency of this function can only be at most 1. Running more than
    1 instance of this function in parallel has the risk of inconsistent table state.
    For example, when 2 instances have deleted the table, one of it re-created first,
    then second will find the external table already exist and fails to re-create.
    """
    # Construct a BigQuery client object.
    client = bigquery.Client()
    table_ref = constants.BQ_TABLE_REF

    # Format of data in GCS
    external_source_format = constants.SOURCE_DATA_FORMAT

    # URI of data in GCS
    source_uris = [constants.SOURCE_URI]

    # Create ExternalConfig object with external source format
    external_config = bigquery.ExternalConfig(external_source_format)

    # Set source_uris that point to your data in Google Cloud
    external_config.source_uris = source_uris

    # table schema
    schema = [
        bigquery.SchemaField("trip_id", "INT64"),
        bigquery.SchemaField("subscriber_type", "STRING"),
        bigquery.SchemaField("bike_id", "INT64"),
        bigquery.SchemaField("bike_type", "STRING"),
        bigquery.SchemaField("start_time", "TIMESTAMP"),
        bigquery.SchemaField("start_station_id", "INT64"),
        bigquery.SchemaField("start_station_name", "STRING"),
        bigquery.SchemaField("end_station_id", "INT64"),
        bigquery.SchemaField("end_station_name", "STRING"),
        bigquery.SchemaField("duration_minutes", "INT64"),
    ]
    external_config.schema = schema

    # partition configs
    partition_options = bigquery.HivePartitioningOptions()
    partition_options.mode = constants.PARTITION_MODE
    partition_options.source_uri_prefix = constants.SOURCE_URI_PREFIX
    external_config.hive_partitioning = partition_options

    # Delete the existing external table if it exists
    try:
        client.delete_table(table_ref, not_found_ok=True)
        print(f"Table {table_ref} deleted.")
    except Exception as e:
        print(f"Error deleting table {table_ref}: {e}")

    # Set the external data configuration of the table
    try:
        table = bigquery.Table(table_ref)
        table.external_data_configuration = external_config
        table = client.create_table(table)  # Make an API request.
    except Conflict:
        print(f"Table {table_ref} already exists.")

    print(
        f"Created table with external source format {table.external_data_configuration.source_format}"
    )
