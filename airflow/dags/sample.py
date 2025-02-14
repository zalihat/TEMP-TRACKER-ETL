from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

# Define a simple Python function to print "Hello"
def print_hello(task_id, **kwargs):
    print(f"Task {task_id}: Hello")

# Define the default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

# Instantiate the DAG
with DAG(
    dag_id='hello_world_dag',
    default_args=default_args,
    description='A simple DAG with 3 tasks printing Hello',
    schedule_interval=None,  # Run manually
    start_date=datetime(2025, 2, 2),
    catchup=False,
) as dag:

    # Define the three tasks
    task_1 = PythonOperator(
        task_id='task_1',
        python_callable=print_hello,
        op_kwargs={'task_id': '1'},
    )

    task_2 = PythonOperator(
        task_id='task_2',
        python_callable=print_hello,
        op_kwargs={'task_id': '2'},
    )

    task_3 = PythonOperator(
        task_id='task_3',
        python_callable=print_hello,
        op_kwargs={'task_id': '3'},
    )

    # Set the dependencies
    task_1 >> task_2 >> task_3
