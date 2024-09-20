def get_name():
    return 'Eric'

def greet(ti):
    name = ti.xcom_pull(task_ids='xcom_push_example')
    print(f"hello {name}")