# BikeShare ETL Pipeline
## Overview
This project implements an ETL pipeline for extracting data from the austin_bikeshare public dataset in BigQuery, transforming the data, storing it in Google Cloud Storage (GCS) in partitioned Parquet format, and then creating an external BigLake table in BigQuery for analysis. The ETL pipeline is automated using Apache Airflow, and the entire project is containerized using Docker for consistency and portability across different environments.

## Project Structure
```
bike/
|-- dags/
|   |-- __init__.py 
|   |-- bikeshare_etl.py           # Airflow DAG for the ETL pipeline
|-- scripts/
|   |-- __init__.py
|   |-- constants.py               # Config file for all settings & constants in scripts
|   |-- create_biglake_tables.py   # Airflow Operator to create external bigquery table
|   |-- extract_bikeshare_trips.py # Airflow Operator to ingest data into GCS using Spark
|   |-- service_account.json       # Service account credentials for Google Cloud
|   |-- sql.txt                    # SQL queries for Task 5: Data Analysis
|-- Dockerfile                     # Dockerfile to containerize the project into Airflow environment
|-- docker-compose.yml             # Docker Compose file to set up Airflow services
|-- requirements.txt               # List of required Python dependencies
|-- README.md                      # Project documentation (this file)
```

### Configuration file
* The configuration file is `constants.py` in the scripts folder. It consists of all configurations and constants used in the airflow operators code. (i.e. `extract_bikeshare_trips.py` and `create_biglake_tables.py`)
* However, for the configurations of the DAG itself (ie schedule_interval, catchup etc), this can be done directly on the DAG and Operators' parameters in `bikeshare_etl.py` in the `dags` folder.

## Pre-requisites
Before you start, make sure you have the following installed:

1. **Docker**: To build and run containers.
1. **Docker Compose**: To orchestrate multi-container applications.
1. **Google Cloud SDK**: To call Google Cloud API via command line

In GCP, make sure to have the following resources ready:

1. Service Account with the following permissions:
    
    * For BigQuery access, either of the following roles:
        * BigQuery Data Editor (roles/bigquery.dataEditor)
        * BigQuery Data Owner (roles/bigquery.dataOwner)
        * BigQuery Admin (roles/bigquery.admin)
    * For Cloud Storage bucket access:
        * storage.buckets.get
        * storage.objects.get
        * storage.objects.list

    The Cloud Storage Storage Admin (roles/storage.admin) predefined Identity and Access Management role includes these permissions.

    Under the tab `KEYS` of the service account, click on `ADD KEY` to create a new key, if not already done so. Create a JSON key and save the file as `service_account.json`. You will need this file later.

2. Create a Google Cloud Storage (GCS) bucket for storing data

3. Create a dataset in Bigquery in the same region as the GCS bucket (Item 2 above). This is for creating an external table linking the data that we ingest in (2).

## Setup
1. Clone this repository to your local disk.
1. In the `scripts` folder, **replace** the `service_account.json` with the one you created in the pre-requisites.
1. In the `scripts` folder, open `constants.py` and modify the config values. In particular, the following parameters:
    * GCS_BUCKET_NAME - Change this to the bucket name you prepared in pre-requisites.
    * BQ_PROJECT_ID - Change this to your project id in GCP
    * BQ_DATASET_ID - Change this to the BigQuery Dataset you created in pre-requisites.

    You may also wish to modify the following parameters to your preference:
    * DATA_NAME - The name you want to give to the ingested data in GCS
    * BQ_TABLE_ID - The name of the external table you create
1. Make sure that your Docker is open and in bash command line, navigate to root directory of this project (i.e. `bike/`) and run the following commands to build the necessary Docker images:
    ```
    docker-compose build
    ```
1. Initialize airflow database with the following command:
    ```
    docker-compose run --rm airflow-webserver airflow db init
    ```
    Note that the data is mounted at `/var/lib/postgresql/data` in your local drive.
    Please ensure the proper access rights are given beforehand. Alternatively, you can mount to a
    different location by modifying this in the `docker-compose.yml` under the `volume` section of the
    `postgres` service.
1. Create an airflow admin user with the following command:
    ```
    docker-compose run --rm airflow-webserver airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
    ```
    You may change the values in the command above to your preference, but please remember what you set.
1. Start Airflow services with the following command:
    ```
    docker-compose up
    ```
    Once all services are started, you can access Airflow Webserver from `localhost:8080`. The port is
    configurable from `docker-compose.yml` as well.
1. Login to Airflow with the user and password you created above. You should see the `bikeshare_etl` pipeline in the UI.

    Observe that the schedule is set to `@daily` as per our code.
    Since we set `catchup=True` in the DAG settings at `bikeshare_etl.py`, Airflow will attempt to backfill from the last partition that ran. In this case, it should be from `2023-12-13` for the data in `2023-12-12` (date of first record in the dataset).

    If the DAG is paused, turn it on to ensure that the DAG  runs on schedule.
1. Once you are done, you can shutdown the set up by pressing `Control+C` to shutdown the containers.
Note that the data are persisted, since we have mounted the data to local disk in the `docker-compose.yml` configuration.

## Manual Backfill
If manual backfilling of data is desired, go to Docker > Containers. Click on the 3 dots button under Actions for the airflow-webserver contain, then `Open in terminal`. 

Use the command below to perform backfill:
```
airflow dags backfill bikeshare_etl -s [start_date] -e [end_date]

For example,
airflow dags backfill bikeshare_etl -s '2024-05-01' -e '2024-05-03'
```

## How the ETL Pipeline Works
### Extraction:

Data is extracted from the `bigquery-public-data.austin_bikeshare.bikeshare_trips` table in BigQuery for the previous day. The data is partitioned by `date` and `hour`.

### Transformation:

The data is processed using Python/Spark.
It is stored in Parquet format on Google Cloud Storage (GCS) with a partitioned directory structure: 
`gs://your-bucket-name/bikeshare/partition_date=YYYY-MM-DD/partition_hour=HH/data.parquet`

Note that the name of the parquet is not necessary `data` but some random syllables. This does not affect the integrity of the data.

### Loading:

An external BigLake table is created in BigQuery that references the partitioned data stored in GCS.
The external table schema matches the data structure, allowing for efficient querying and analysis.

### Scheduling:

The entire pipeline is automated with Apache Airflow. The DAG is scheduled to run once per day, extracting, transforming, and storing the data for the previous day.

### Concurrency

The pipeline is designed to be able to run multiple instances concurrently. To configure the number of
maximum concurrent run, go to code of the DAG at `bikeshare_etl.py`. In the definition of the DAG,
configure the value of `max_active_runs`. Take note however that for the `create_table` operator,
it can only run 1 instance at any time, as it runs the risk of causing inconsistent table state if
multiple instances of the operator run concurrently.

## SQL Queries for Data Analysis
After the data is loaded into BigQuery, we perform data analysis with the data directly on Bigquery.
The SQLs can be found in `scripts/sql.txt`. Before you run any of the SQLs on Bigquery, please remember to change the table reference to the one you have created.