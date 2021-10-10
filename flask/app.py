from flask import Flask
from flask import request
from os import getenv
import psycopg2 as pg






db_pass = getenv('DB_PASS')
db_user = getenv('DB_USER')
db_maindb = getenv('DB_MAINDB')
db_host = getenv('DB_HOST')
db_port = getenv('DB_PORT')

def add_action(value):
    conn = pg.connect(host=cf.db_host, dbname=cf.db_maindb, user=cf.db_user, password=cf.db_pass, port=cf.db_port)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"insert into public.log (value) values('{value}')")
    finally:
        conn.close()

app = Flask(__name__)

@app.route('/', methods = ["POST"])
def test():
    value = str(request.json).replace("'", "`")
    add_action(value)
    return {"ok": True}
#    return "hello from docker"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)