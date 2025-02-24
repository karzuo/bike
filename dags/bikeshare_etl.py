import sys
import os

# Add the path to the 'scripts' folder to sys.path so it can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from airflow import DAG
from datetime import datetime
from airflow.operators.python import PythonOperator
from scripts.extract_bikeshare_trips import extract_bikeshare_trips
from scripts.create_biglake_tables import create_biglake_table


with DAG(
    dag_id="bikeshare_etl",
    start_date=datetime(year=2023, month=12, day=13, hour=0, minute=0),
    schedule_interval="@daily",
    catchup=True,
    max_active_runs=5,
    render_template_as_native_obj=True,
) as dag:

    extract_data = PythonOperator(
        dag=dag,
        task_id="extract_data",
        python_callable=extract_bikeshare_trips,
        op_kwargs={"date_of_run": "{{ ds }}"},
    )

    create_table = PythonOperator(
        dag=dag, task_id="create_table", python_callable=create_biglake_table
    )

    # Set task dependencies
    extract_data >> create_table
