from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tasks')))

# from tasks.extract import extract_weather_data
from utils.utils import extract_weather_data
# Define the load task
def load_to_postgres_xcom(**kwargs):
    """
    Load the transformed data directly into PostgreSQL using XCom.
    """
    # Get the transformed data from XCom
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_weather_data')
    # Connect to PostgreSQL
    pg_hook = PostgresHook(postgres_conn_id='postgres_localhost')
    
    # SQL Insert statement
    insert_query = """
    INSERT INTO processed_weather_data (location, region, country, lat, lon, "localtime",
       temperature_c, temperature_f, feelslike_c, feelslike_f, date)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
    """
    
    # Insert rows into PostgreSQL
    for row in transformed_data:
        pg_hook.run(insert_query, parameters=(row['location'], row['region'], row['country'],row['lat'], row['lon'], row['localtime'], row['temperature_c'], row['temperature_f'], row['feelslike_c'], row['feelslike_f'], row['date']   ))

# Define default arguments
default_args = {
    'owner': 'zalihat',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 6),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

# Create the DAG
dag = DAG('Temp_elt_postgres', default_args=default_args, schedule_interval=timedelta(days=1))

# Define the task using PythonOperator
extract = PythonOperator(
    task_id='extract_weather_data',
    python_callable=extract_weather_data,  
    dag=dag,
)

move_files = BashOperator(
    task_id="move_files",
    bash_command="mv /opt/airflow/data/raw /shared-data/raw",
)
transform = SparkSubmitOperator(
    task_id='transform_weather_data',
    application='/opt/airflow/utils/transform.py',  # Path to your Spark job
    conn_id='spark_default',  # Airflow Spark connection
    executor_cores=1,
    executor_memory='1g',
    driver_memory='1g',
    conf={
        "spark.jars": "/shared-data/postgresql-42.7.5.jar",
        "spark.driver.extraClassPath": "/shared-data/postgresql-42.7.5.jar",
        "spark.executor.extraClassPath": "/shared-data/postgresql-42.7.5.jar"
    },
    verbose=True,
    dag=dag
)
create_table = PostgresOperator(
        task_id='create_processed_weather_data_table',
        postgres_conn_id='postgres_localhost',
        sql="""
            create table if not exists processed_weather_data (
                location VARCHAR(50),
                region VARCHAR(50),
                country VARCHAR(50),
                lat DOUBLE PRECISION,
                lon DOUBLE PRECISION,
                "localtime" TIMESTAMP,
                temperature_c DOUBLE PRECISION ,
                temperature_f DOUBLE PRECISION,
                feelslike_c DOUBLE PRECISION,
                feelslike_f DOUBLE PRECISION,
                date DATE ,
                primary key ("localtime", location)
            )
        """
    )




extract >> create_table >> transform 