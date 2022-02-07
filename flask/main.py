# -*- coding: utf-8 -*-
import json
from datetime import datetime
import uuid
import config
import azure.cosmos.cosmos_client as cosmos_client
from flask import request
from flask import Flask



def is_target(text, **kwargs):
    return 'Уточнение заказа' in text

def parse_product_info(json_txt, **kwargs):
    try:
        content = []
        target_text = json_txt['callback_query']['message']['text']
        block_list = target_text.split("●")
        for block in block_list:
            if "Товары:" in block and "Итого:" not in block:
                products = block.replace("Товары:", "").strip().split("———")
                for product in products:
                    tmp = [i for i in product.split("\n") if i != '']
                    name = tmp[0]
                    cnt = tmp[1].split('=')[0].split('x')[0].strip().split(' ')[0]
                    cost = tmp[1].split('=')[0].split('x')[1].strip().split(' ')[0]
                    content.append({'name': name, 'cnt': cnt, 'cost': cost})
        return content
    except:
        # отправить в бд в таблицу ошибок данный пример, чтобы потом его разобрать
        print("error")

def parse_customer_info(json_txt, **kwargs):
    try:
        return json_txt['callback_query']['from']
    except:
        print("error")

def parse_date_info(json_txt, **kwargs):
    try:
        return datetime.fromtimestamp(int(json_txt['callback_query']['message']['date'])).strftime('%d-%m-%Y %H:%M:%S')
    except:
        print("error")

def parse_delivery_info(json_txt, **kwargs):
    try:
        content = {}
        target_text = json_txt['callback_query']['message']['text']
        block_list = target_text.split("●")
        for block in block_list:
            if "Способ доставки" in block and "Итого:" not in block:
                tmp = [i for i in block.replace("Способ доставки:", "").replace("Адрес доставки:", "").strip().split('\n') if i != '']
                try:
                    delivery_type = tmp[0].split('→')[1].strip()
                    content['delivery_type'] = delivery_type
                except:
                    pass
                try:
                    delivery_address = tmp[1]
                    content['delivery_address'] = delivery_address
                except:
                    pass
                try:
                    delivery_phone = tmp[2]
                    content['delivery_phone'] = delivery_phone
                except:
                    pass
        return content
    except:
        # отправить в бд в таблицу ошибок данный пример, чтобы потом его разобрать
        print("error")

def parse_bill_type_info(json_txt, **kwargs):
    try:
        target_text = json_txt['callback_query']['message']['text']
        block_list = target_text.split("●")
        for block in block_list:
            if "Способ оплаты:" in block and "Итого:" not in block:
                tmp = block.replace("Способ оплаты:", "").replace('\n','').strip()
        return tmp
    except:
        # отправить в бд в таблицу ошибок данный пример, чтобы потом его разобрать
        print("error")

def parse_results_info(json_txt, **kwargs):
    try:
        content = {}
        target_text = json_txt['callback_query']['message']['text']
        block_list = target_text.split("●")
        for block in block_list:
            if "Итого:" in block:
                tmp = [i for i in block.replace("Итого:", "").strip().split('\n') if i != '']
                for i in tmp:
                    if 'Товары:' in i:
                        try:
                            product_cost = i.replace('Товары:', '').strip().split(' ')[0]
                            content['products_cost'] = product_cost
                        except:
                            pass
                    elif 'Способ доставки:' in i:
                        try:
                            delivery_cost = i.replace('Способ доставки:', '').strip().split(' ')[0]
                            content['delivery_cost'] = delivery_cost
                        except:
                            pass
                    elif 'Способ оплаты:' in i:
                        try:
                            payment_method_cost = i.replace('Способ оплаты:', '').strip().split(' ')[0]
                            content['payment_method_cost'] = payment_method_cost
                        except:
                            pass
        return content
    except:
        # отправить в бд в таблицу ошибок данный пример, чтобы потом его разобрать
        print("error")

def load_to_cosmos(data:dict, **kwargs):
    HOST = config.settings['host']
    MASTER_KEY = config.settings['master_key']
    DATABASE_ID = config.settings['database_id']
    CONTAINER_ID = config.settings['container_id']

    client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
    db = client.get_database_client(DATABASE_ID)
    container = db.get_container_client(CONTAINER_ID)
    container.create_item(body=data)

def main_process(log, **kwargs):
    if is_target(log):
        try:
            json_log = json.loads(log.replace("False", "false").replace("True", "true"), strict=False)

            result = {}

            result['id'] = str(uuid.uuid4())
            result['customer'] = parse_customer_info(json_log)
            result['date'] = parse_date_info(json_log)
            result['product'] = parse_product_info(json_log)
            result['delivery'] = parse_delivery_info(json_log)
            result['bill_type'] = parse_bill_type_info(json_log)
            result['results'] = parse_results_info(json_log)

            load_to_cosmos(result)
        except:
            pass
    else:
        pass

app = Flask(__name__)

@app.route('/', methods = ["POST", "GET"])
def main():
    if request.method == "POST":
        main_process(str(request.json))
        return {"ok": True}
    else:
        return "Hello from grigoryBzr"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)