from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

# Define default args
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

# Define the DAG
dag = DAG(
    "pyspark_example",
    default_args=default_args,
    schedule_interval="@daily",
    catchup=False,
)

# PySpark job submission
spark_job = SparkSubmitOperator(
    task_id="run_pyspark_job",
    application="/opt/airflow/dags/scripts/pyspark_job.py",  # Path to PySpark script
    conn_id="spark_default",  # Airflow connection to Spark
    executor_cores=1,
    executor_memory="1g",
    driver_memory="1g",
    name="pyspark_airflow_job",
    verbose=True,
    dag=dag,
)

# Task execution
spark_job
