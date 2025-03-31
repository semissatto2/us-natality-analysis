from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitJobOperator,
    DataprocDeleteClusterOperator,
)
from airflow.providers.google.cloud.hooks.gcs import GCSHook
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from google.cloud import bigquery
import pandas as pd
import os
from datetime import datetime
from airflow.utils.trigger_rule import TriggerRule

# Variables
TABLE_SOURCE = "`bigquery-public-data.samples.natality`"
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
GCP_GCS_BUCKET = os.environ.get("GCP_GCS_BUCKET")
STATE_LOOKUP_URL = r"https://docs.google.com/uc?export=download&id=1dsVF__ZPD-40eZLVhedrGn-wWDCJX6bU"
RACE_LOOKUP_URL = r"https://docs.google.com/uc?export=download&id=17o8e1eh7XkHk61P5JuBAi2JhFvnUt4tJ"
GCP_CLUSTER_NAME = "us-natality-cluster"
GCP_REGION = "us-central1"
LOCAL_PYSPARK_SCRIPT_PATH = "/opt/airflow/dags/pyspark_to_bq.py"
GCP_PYSPARK_SCRIPT_PATH = f"scripts/pyspark_to_bq.py"
GCP_PYSPARK_SCRIPT_FULLPATH = "gs://" + GCP_GCS_BUCKET + r"/" + GCP_PYSPARK_SCRIPT_PATH


def build_query(month):
    """
    Define the SQL query, selecting only the columns of interest for analysis.
    """
    query = f"""
    SELECT year, month, child_race, state, gestation_weeks, is_male, weight_pounds
    FROM {TABLE_SOURCE}
    WHERE month = {month}
    LIMIT 100
    """
    return query


def query_to_gcs(month, **kwargs):
    """
    Optimized function to query BigQuery and save the result to GCS.
    """
    # BigQuery configurations
    project_id = GCP_PROJECT_ID
    bucket_name = GCP_GCS_BUCKET
    gcs_path = f'natality/data_month_{month}.csv'
    
    # Initializing BigQuery client
    client = bigquery.Client(project=GCP_PROJECT_ID)
    
    # Executing the query
    query = build_query(month)
    query_job = client.query(query)
    df = query_job.to_dataframe()
    
    # Output file path
    output_file = f'/tmp/temp_output_{month}.csv'
    
    # Saving the results
    df.to_csv(output_file, index=False)
    
    # Upload to GCS
    gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
    gcs_hook.upload(GCP_GCS_BUCKET, gcs_path, output_file)
    
    # Deleting the temporary file
    os.remove(output_file)
    
    return f'Query executed for month {month} and results uploaded to GCS.'


def upload_local_file_to_gcs(output_file):
    """
    Uploads a local file to GCS and removes the local file after uploading.
    """
    gcs_path = f'natality-lookup_tables/{output_file.replace("/tmp/", "")}'
    gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
    gcs_hook.upload(GCP_GCS_BUCKET, gcs_path, output_file)
    os.remove(output_file)

def upload_local_spark_file_to_gcs(output_file):
    """
    Uploads a local file to GCS and removes the local file after uploading.
    """
    gcs_path = GCP_PYSPARK_SCRIPT_PATH
    gcs_hook = GCSHook(gcp_conn_id='google_cloud_default')
    gcs_hook.upload(GCP_GCS_BUCKET, gcs_path, output_file)


# DAG configurations
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 11, 1),
}

# This DAG downloads data in batches, chunked by year.  
# The years are processed in parallel.  
# Due to computational resource limitations, we can't process all years simultaneously.  
# Therefore, we first process odd months, followed by even months.  
odd_months_to_process = list(range(1, 13, 2))
even_months_to_process = list(range(2, 13, 2))

with DAG(
    'natality_web_data_to_gcs',
    default_args=default_args,
    schedule_interval=None,
) as dag:
    
    # Define dummy tasks
    start = BashOperator(
        task_id="start",
        bash_command='echo "Started!"'
    )

    joint1 = BashOperator(
        task_id="joint1",
        bash_command='echo "Joint!"'
    )

    joint2 = BashOperator(
        task_id="joint2",
        bash_command='echo "Joint2!"'
    )

    joint3 = BashOperator(
        task_id="joint3",
        bash_command='echo "Joint3!"'
    )

    joint4 = BashOperator(
        task_id="joint4",
        bash_command='echo "Joint4!"'
    )

    end = BashOperator(
        task_id="end",
        bash_command='echo "End!"'
    )

    download_state_lookup = BashOperator(
        task_id="download_state_lookup",
        bash_command=f'wget --no-check-certificate "{STATE_LOOKUP_URL}" -O /tmp/state_lookup.csv'
    )

    task_upload_state_lookup = PythonOperator(
        task_id='upload_state_lookup',
        python_callable=upload_local_file_to_gcs,
        op_args=['/tmp/state_lookup.csv']
    )

    download_race_lookup = BashOperator(
        task_id="download_race_lookup",
        bash_command=f'wget --no-check-certificate "{RACE_LOOKUP_URL}" -O /tmp/race_lookup.csv'
    )

    task_upload_race_lookup = PythonOperator(
        task_id='upload_race_lookup',
        python_callable=upload_local_file_to_gcs,
        op_args=['/tmp/race_lookup.csv']
    )

    # Creating a task for each year (odd months)
    query_tasks_odd = []
    for month in odd_months_to_process:
        query_task_odd = PythonOperator(
            task_id=f'query_and_upload_to_gcs_{month}',
            python_callable=query_to_gcs,
            op_args=[month],
            provide_context=True,
        )
        query_tasks_odd.append(query_task_odd)

    # Creating a task for each year (even months)
    query_tasks_even = []
    for month in even_months_to_process:
        query_task_even = PythonOperator(
            task_id=f'query_and_upload_to_gcs_{month}',
            python_callable=query_to_gcs,
            op_args=[month],
            provide_context=True,
        )
        query_tasks_even.append(query_task_even)
    
    # Create Dataproc Cluster
    create_cluster = DataprocCreateClusterOperator(
        task_id='create_dataproc_cluster',
        project_id=GCP_PROJECT_ID,
        cluster_name=GCP_CLUSTER_NAME,
        region=GCP_REGION,
        num_masters=1,
        num_workers=2,
        master_machine_type='n1-standard-2',
        worker_machine_type='n1-standard-2'
    )

    task_upload_pyspark_script = PythonOperator(
        task_id='upload_pyspark_script',
        python_callable=upload_local_spark_file_to_gcs,
        op_args=[LOCAL_PYSPARK_SCRIPT_PATH]
    )

    # Submit PySpark Job
    submit_job = DataprocSubmitJobOperator(
        task_id='submit_pyspark_job',
        project_id=GCP_PROJECT_ID,
        job={
            'reference': {'project_id': GCP_PROJECT_ID},
            'placement': {'cluster_name': GCP_CLUSTER_NAME},
            'pyspark_job': {'main_python_file_uri': GCP_PYSPARK_SCRIPT_FULLPATH}
        },
        region=GCP_REGION,
    )

    # Delete Dataproc Cluster
    delete_cluster = DataprocDeleteClusterOperator(
        task_id='delete_dataproc_cluster',
        project_id=GCP_PROJECT_ID,
        cluster_name=GCP_CLUSTER_NAME,
        region=GCP_REGION,
        trigger_rule=TriggerRule.ALL_DONE
    )
    
    # Task dependencies
    start >> [download_state_lookup, download_race_lookup] >> joint1
    joint1 >> [task_upload_state_lookup, task_upload_race_lookup] >> joint2
    joint2 >> query_tasks_odd >> joint3
    joint3 >> query_tasks_even >> joint4
    joint4 >> task_upload_pyspark_script >> create_cluster >> submit_job >> delete_cluster
    delete_cluster >> end
