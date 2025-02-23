from google.cloud import bigquery

# Construct a BigQuery client object.
client = bigquery.Client()

# TODO make configurable
table_id = "bike-451619.tech_homework.bikeshare"

# Format of data in GCS
external_source_format = "PARQUET"

# URI of data in GCS
source_uris = ["gs://bike-share-hw/bikeshare/*"]

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
external_config.schema=schema

# # partition configs
partition_options=bigquery.HivePartitioningOptions()
partition_options.mode="AUTO"
partition_options.source_uri_prefix='gs://bike-share-hw/bikeshare/'
external_config.hive_partitioning=partition_options

# Delete the existing external table if it exists
try:
    client.delete_table(table_id, not_found_ok=True)
    print(f"Table {table_id} deleted.")
except Exception as e:
    print(f"Error deleting table {table_id}: {e}")

# Set the external data configuration of the table
table = bigquery.Table(table_id)
table.external_data_configuration = external_config
table = client.create_table(table)  # Make an API request.

print(f"Created table with external source format {table.external_data_configuration.source_format}")