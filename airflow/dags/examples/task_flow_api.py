from airflow.decorators import dag, task 
from datetime import datetime, timedelta

import pendulum

default_args = {
    'owner': 'Eric',
    'retries': 5,
    'retry_delay': timedelta(minutes=5)
}
@dag(dag_id='dag_with_taskflow_api',
     default_args=default_args,
     start_date=pendulum.today('UTC').add(days=-1),
     schedule='@daily',
     catchup=False
     )

def hello_world_etl():
    
    @task(multiple_outputs=True)
    def get_name():
        return {
            'first_name': 'eric',
            'last_name': 'chee'
        }
    
    @task()
    def get_age(): 
        return 27
    
    @task()
    def greet(first_name, last_name, age):
        print(f"{first_name}, {last_name}, {age}")
        
    name_dict = get_name()
    age = get_age()
    
    greet(first_name=name_dict['first_name'], 
          last_name=name_dict['last_name'],
          age=age)
    
greet_dag = hello_world_etl()