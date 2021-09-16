import psycopg2 as pg
import config as cf


def add_action(value):
    conn = pg.connect(host=cf.db_host, dbname=cf.db_maindb, user=cf.db_user, password=cf.db_pass, port=cf.db_port)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"insert into public.log (value) values('{value}')")
    finally:
        conn.close()