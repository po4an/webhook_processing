from flask import Flask
from flask import request
import config as cfg
import psycopg2 as pg


# config
db_pass = cfg.DB_PASS
db_user = cfg.DB_USER
db_maindb = cfg.DB_MAINDB
db_host = cfg.DB_HOST
db_port = cfg.DB_PORT
cert = cfg.CERT
cert_key = cfg.CERT_KEY
token = cfg.TOKEN



app = Flask(__name__)
context = (cert, cert_key)


def add_action(value):
    conn = pg.connect(host=db_host, dbname=db_maindb, user=db_user, password=db_pass, port=db_port)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"insert into public.log (value) values('{value}')")
    finally:
        conn.close()




@app.route('/' + token, methods = ["POST", "GET"])
def test():
    if request.method == "POST":
        value = str(request.json).replace("'", "`")
        add_action(value)
        return {"ok": True}
    else:
        return "Hello from grigoryBzr"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8443, ssl_context = context, debug=True)
