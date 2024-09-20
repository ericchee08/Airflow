def get_name(ti):
    ti.xcom_push(key='first_name', value='Eric')
    ti.xcom_push(key='last_name', value='Chee')

def greet(ti):
    first_name = ti.xcom_pull(task_ids='xcom_push_example', key='first_name')
    last_name = ti.xcom_pull(task_ids='xcom_push_example', key='last_name')
    print(f"hello {first_name} {last_name}")