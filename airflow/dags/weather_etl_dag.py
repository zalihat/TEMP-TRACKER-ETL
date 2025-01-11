from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tasks')))

from tasks.extract import extract_weather_data
from tasks.transform import transform_weather_data
# from tasks.extract import extract_weather_data



# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 3),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG('Temp_elt', default_args=default_args, schedule_interval=timedelta(days=1))

# Define the task using PythonOperator
t1 = PythonOperator(
    task_id='extract_weather_data',
    python_callable=extract_weather_data,  
    dag=dag,
)
t2 = PythonOperator(
    task_id='transformm_weather_data',
    python_callable=transform_weather_data,
    dag=dag,
)
t1 >> t2 