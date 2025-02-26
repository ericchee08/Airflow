from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
import pendulum

# Define default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'start_date': pendulum.today('UTC').add(days=-1),
    'retries': 1,
}

# Create the DAG
with DAG(
    'simple_postgres_dag',
    default_args=default_args,
    description='A simple DAG to interact with PostgreSQL',
    schedule=None,  # Manual trigger
    catchup=False,
) as dag:

    # Task 1: Create a table if it doesn't exist
    create_table = SQLExecuteQueryOperator(
        task_id='create_table',
        conn_id='eric_db',  # Airflow connection ID
        sql='''
        CREATE TABLE IF NOT EXISTS my_table (
            id SERIAL PRIMARY KEY,
            name VARCHAR(50),
            age INT
        );
        '''
    )

    # Task 2: Insert data into the table
    insert_data = SQLExecuteQueryOperator(
        task_id='insert_data',
        conn_id='eric_db',
        sql='''
        INSERT INTO my_table (name, age) VALUES ('John Doe', 30);
        '''
    )

    # Task 3: Fetch data from the table
    fetch_data = SQLExecuteQueryOperator(
        task_id='fetch_data',
        conn_id='eric_db',
        sql='SELECT * FROM my_table;',
    )

    # Define task dependencies
    create_table >> insert_data >> fetch_data
