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

#команда для добавления вебхука
#curl --location --request POST 'https://api.telegram.org/bot1659154070:AAGjwQ5B9eqJcIs-9PaDjKID8Qn9-5v11vY/setWebhook' --header 'Content-Type: application/json' --data-raw '{"url": "https://0a46-95-181-245-233.ngrok.io"}'


if __name__ == '__main__':
    app.run(host='0.0.0.0')