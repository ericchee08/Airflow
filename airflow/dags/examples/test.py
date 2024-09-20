from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from python_callables.examples import print_airflow_variable, xcom

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

python_task = PythonOperator(
    task_id='python_operator_print_airflow_variable',
    python_callable=print_airflow_variable.print_airflow_variable_example_var,
    op_kwargs={ 'example_var' : "{{ var.value.get('example_variable') }}" },
    dag=dag
)

bash_task = BashOperator(
    task_id='bash_operator_echo_airflow_variable',
    bash_command="echo '{{ var.value.get('example_variable') }}'",
    dag=dag
)

xcom_task_push = PythonOperator(
    task_id="xcom_push_example",
    python_callable=xcom.get_name
)

xcom_task_pull = PythonOperator(
    task_id='xcom_pull_example',
    python_callable=xcom.greet
)



# Set the task order
python_task >> bash_task >> xcom_task_push >> xcom_task_pull
