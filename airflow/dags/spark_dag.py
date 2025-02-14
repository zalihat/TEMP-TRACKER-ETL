from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2025, 2, 3),
    'retries': 1
}

dag = DAG(
    'spark_job_dag',
    default_args=default_args,
    schedule_interval='@daily',
    catchup=False
)

spark_task = SparkSubmitOperator(
    task_id='run_spark_job',
    application='/opt/spark/app.py',  # Path to your Spark job
    conn_id='spark_default',  # Airflow Spark connection
    executor_cores=1,
    executor_memory='1g',
    driver_memory='1g',
    verbose=True,
    dag=dag
)

spark_task
