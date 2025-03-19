from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

# Define the DAG
dag = DAG(
    dag_id="simple_bash_dag",
    start_date=datetime(2025, 2, 2),
    schedule_interval=None,  # Runs manually
    catchup=False,
)

# Define a task using BashOperator
task_1 = BashOperator(
    task_id="print_message",
    bash_command="echo 'Hello from Airflow!'",
    dag=dag,  # Pass the DAG to the operator
)

task_1