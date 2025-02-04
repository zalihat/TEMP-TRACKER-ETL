from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
import sys
import os

# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'tasks')))

from tasks.extract import extract_weather_data
from tasks.transform import transform_weather_data
# from tasks.extract import extract_weather_data

# Define the transform task
def transform_weather_data_xcom(**kwargs):
    """
    Perform data transformation and return the transformed data.
    """
    # Assuming transform_weather_data returns a pandas DataFrame
    transformed_data = transform_weather_data()  # This should be your transformation logic
    
    # Convert the DataFrame to a list of dictionaries for XCom
    return transformed_data.to_dict(orient='records')


# Define the load task
def load_to_postgres_xcom(**kwargs):
    """
    Load the transformed data directly into PostgreSQL using XCom.
    """
    # Get the transformed data from XCom
    ti = kwargs['ti']
    transformed_data = ti.xcom_pull(task_ids='transform_weather_data')
    
    # Connect to PostgreSQL
    from airflow.providers.postgres.hooks.postgres import PostgresHook
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
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 3),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG('Temp_elt_postgres', default_args=default_args, schedule_interval=timedelta(days=1))

# Define the task using PythonOperator
extract = PythonOperator(
    task_id='extract_weather_data',
    python_callable=extract_weather_data,  
    dag=dag,
)

transform = PythonOperator(
    task_id='transform_weather_data',
    python_callable=transform_weather_data_xcom,
    provide_context=True,  # Allow access to XComs
    dag=dag,
)

load = PythonOperator(
    task_id='load_to_postgres',
    python_callable=load_to_postgres_xcom,
    provide_context=True,
    dag=dag,
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
extract >> transform >> create_table >> load