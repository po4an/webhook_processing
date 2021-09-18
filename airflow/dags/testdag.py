from airflow import DAG
#from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime
import psycopg2 as pg
import pandas as pd
import pandas.io.sql as sqlio



default_args = {
    "owner": "grigory.bezruchenko",
#    "depends_on_past": False,
    "start_date": datetime(2021, 9, 16),
    "provide_context": True
#    "email": ["airflow@airflow.com"],
#    "email_on_failure": False,
#    "email_on_retry": False,
#    "retries": 1,
#    "retry_delay": timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

def extract_metadata(**kwargs):
    ti = kwargs['ti']
    conn = pg.connect(host='main_db', dbname='hqddb', user='hqduser', password='hqdpassword', port='5432')
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"select max(date_to) from public.checkpoints")
                date_from = str(cur.fetchone()[0])
    finally:
        conn.close()
    if date_from == 'None':
        date_from = '2020-01-01 00:00:00'
    print(date_from)
    ti.xcom_push(key='date_from', value=date_from)

def extract_raw_data(**kwargs):
    ti = kwargs['ti']

    date_from = ti.xcom_pull(key='date_from', task_ids=['extract_metadata'])[0]
    print(date_from)
    date_to = datetime.now()

    conn = pg.connect(host='main_db', dbname='hqddb', user='hqduser', password='hqdpassword', port='5432')
    try:
        with conn:
            sql = f"select * from public.log where load_dttm between '{date_from}'::timestamp and '{date_to}'::timestamp;"
            raw_data = sqlio.read_sql_query(sql, conn)
    finally:
        conn.close()
    print(raw_data)
    print(date_to)
    ti.xcom_push(key='date_to', value=date_to)
    ti.xcom_push(key='raw_data', value=raw_data)

def transform_data(**kwargs):
#    ti = kwargs['ti']
#    raw_data = ti.xcom_pull(key='raw_data', task_ids=['2'])[0]
    pass

def load_data(**kwargs):
    pass

def clear_log(**kwargs):
    ti = kwargs['ti']
    date_from = ti.xcom_pull(key='date_from', task_ids=['extract_metadata'])[0]
    date_to = ti.xcom_pull(key='date_to', task_ids=['extract_raw_data'])[0]
    print(date_from)
    print(date_to)
    conn = pg.connect(host='main_db', dbname='hqddb', user='hqduser', password='hqdpassword', port='5432')
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"delete from public.log where load_dttm between '{date_from}'::timestamp and '{date_to}'::timestamp;")
    finally:
        conn.close()

def update_metadata(**kwargs):
    ti = kwargs['ti']
    date_from = ti.xcom_pull(key='date_from', task_ids=['extract_metadata'])[0]
    date_to = ti.xcom_pull(key='date_to', task_ids=['extract_raw_data'])[0]
    print(date_from)
    print(date_to)
    conn = pg.connect(host='main_db', dbname='hqddb', user='hqduser', password='hqdpassword', port='5432')
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"insert into public.checkpoints (date_from, date_to) values('{date_from}'::timestamp, '{date_to}'::timestamp);")
    finally:
        conn.close()



with DAG("regular_load", description="regular_load", default_args=default_args, schedule_interval='*/5 * * * *', catchup=False) as dag:
    extract_metadata = PythonOperator(
        task_id="extract_metadata",
        python_callable=extract_metadata
    )

    extract_raw_data = PythonOperator(
        task_id="extract_raw_data",
        python_callable=extract_raw_data
    )

    transform_data = PythonOperator(
        task_id="transform_data",
        python_callable=transform_data
    )

    load_data = PythonOperator(
        task_id="load_data",
        python_callable=load_data
    )

    clear_log = PythonOperator(
        task_id="clear_log",
        python_callable=clear_log
    )

    update_metadata = PythonOperator(
        task_id="update_metadata",
        python_callable=update_metadata
    )
extract_metadata >> extract_raw_data >> transform_data >> load_data >> clear_log >> update_metadata


