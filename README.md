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

## Pre-requisites
Before you start, make sure you have the following installed:

1. **Docker**: To build and run containers.
1. **Docker Compose**: To orchestrate multi-container applications.

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

2. A Google Cloud Storage (GCS) bucket for storing data

3. A dataset in Bigquery in the same region as the GCS bucket (Item 2 above). This is for creating an external table linking the data that we ingest in (2).

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
1. Make sure that your Docker is open and in bash command line, navigate to root directory of this project and run the following commands to build the necessary Docker images:
    ```
    docker-compose build
    ```
1. Initialize airflow database with the following command:
    ```
    docker-compose run --rm airflow-webserver airflow db init
    ```
1. Create an airflow admin user with the following command:
    ```
    docker-compose run --rm airflow-webserver airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
    ```
    You may change the values in the command above to your preference, but please remember what you set.
1. Start Airflow services with the following command:
    ```
    docker-compose up
    ```
    Once all services are started, you can access Airflow Webserver from `localhost:8080`
1. Login to Airflow with the user and password you created above. You should see the `bikeshare_etl` pipeline in the UI.

    Observe that the schedule is set to `@daily` as per our code.
    Since we set `catchup=True` in the DAG settings at `bikeshare_etl.py`, Airflow will attempt to backfill from the last partition that ran. In this case, it should be from `2023-12-13` for the data in `2023-12-12` (date of first record in the dataset)





bash
Copy
git clone https://github.com/your-repo-name.git
cd your-repo-name
2. Set up Google Cloud Authentication
The ETL pipeline will need to authenticate using a service account. Follow these steps:

Create a service account in Google Cloud with the necessary permissions (BigQuery, GCS access).
Download the service account JSON key file and place it in the scripts/ directory as service_account.json.
3. Configure Airflow (Docker Compose)
The project uses Docker Compose to run Apache Airflow. To configure the services:

Open the docker-compose.yml file and ensure the Airflow web server and scheduler configurations are correct.
The Airflow web server will be available at http://localhost:8080 by default.
4. Install Python Dependencies
Install the necessary Python dependencies by using requirements.txt:

bash
Copy
pip install -r requirements.txt
5. Build and Start Docker Containers
Once everything is set up, build the Docker container and start the services using Docker Compose:

bash
Copy
docker-compose up --build
This will:

Build the Airflow Docker containers (web server and scheduler).
Start the services and expose the Airflow UI at http://localhost:8080.
6. Trigger the Airflow DAG
Once the services are up and running, you can trigger the ETL pipeline DAG from the Airflow UI:

Open the Airflow UI at http://localhost:8080.
Find the DAG bikeshare_etl and trigger it manually or wait for it to run on the next scheduled time (daily).
7. Monitor DAG Execution
You can monitor the execution of the ETL pipeline in the Airflow UI. Check for task success, failure, or logs for debugging.

How the ETL Pipeline Works
Extraction:

Data is extracted from the bigquery-public-data.austin_bikeshare.bikeshare_trips table in BigQuery for the previous day.
The data is partitioned by date and hour.
Transformation:

The data is processed using Python/Spark.
It is stored in Parquet format on Google Cloud Storage (GCS) with a partitioned directory structure: gs://your-bucket-name/bikeshare/YYYY-MM-DD/HH/data.parquet.
Loading:

An external BigLake table is created in BigQuery that references the partitioned data stored in GCS.
The external table schema matches the data structure, allowing for efficient querying and analysis.
Scheduling:

The entire pipeline is automated with Apache Airflow. The DAG is scheduled to run once per day, extracting, transforming, and storing the data for the previous day.
Running the Project Without Docker (Optional)
If you prefer not to use Docker, you can run the Airflow services locally by setting up Apache Airflow on your machine.

Install Apache Airflow using pip:

bash
Copy
pip install apache-airflow
Set up the Airflow environment (refer to the Airflow documentation for details).

Initialize the Airflow database:

bash
Copy
airflow db init
Start the Airflow web server:

bash
Copy
airflow webserver --port 8080
Start the Airflow scheduler:

bash
Copy
airflow scheduler
SQL Queries for Data Analysis
After the data is loaded into BigQuery, you can run the following SQL queries to analyze the data:

Find the total number of trips for each day.
Calculate the average trip duration for each day.
Identify the top 5 stations with the highest number of trip starts.
Find the average number of trips per hour of the day.
Determine the most common trip route (start station to end station).
Calculate the number of trips each month.
Find the station with the longest average trip duration.
Find the busiest hour of the day (most trips started).
Identify the day with the highest number of trips.
License
This project is licensed under the MIT License.

Acknowledgments
Google Cloud for providing the BigQuery and GCS services.
Apache Airflow for the orchestration of the ETL pipeline.










* create a dataset in same location as the gcs bucket if not yet created.
* big lake not created due to costs, but is just one small step

* set google credentials env var


Setup Airflow:
generate fernet key and replace in docker-compose
docker-compose run --rm airflow-webserver airflow db init
docker-compose run --rm airflow-webserver airflow users create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin
docker-compose up
