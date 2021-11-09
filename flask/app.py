import psycopg2 as pg
from flask import request
from flask import Flask


app = Flask(__name__)

# config
db_host='postgres'
db_user='postgres'
db_pass='postgres'
db_port='5432'
db_maindb='postgres'
port = 5432


def add_action(value):
    conn = pg.connect(host=db_host, dbname=db_maindb, user=db_user, password=db_pass, port=db_port)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"insert into public.log (value) values('{value}')")
    finally:
        conn.close()




@app.route('/', methods = ["POST", "GET"])
def test():
    if request.method == "POST":
        value = str(request.json).replace("'", "`")
        add_action(value)
        return {"ok": True}
    else:
        return "Hello from grigoryBzr"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = 443)