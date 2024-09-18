from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

# Define default arguments
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

# Define the DAG
dag = DAG(
    'test_dag',
    default_args=default_args,
    description='A simple test DAG',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
)

def print_hello():
    print('Hello, world!')

hello_task = PythonOperator(
    task_id='print_hello',
    python_callable=print_hello,
    dag=dag,
)

# Set the task order
hello_task
