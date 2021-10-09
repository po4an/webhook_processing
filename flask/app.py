from flask import Flask
from flask import request
from utils import add_action


app = Flask(__name__)

@app.route('/', methods = ["POST"])
def test():
    value = str(request.json).replace("'", "`")
    add_action(value)
    return {"ok": True}
#    return "hello from docker"


if __name__ == '__main__':
    app.run(host='0.0.0.0')