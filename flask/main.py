# -*- coding: utf-8 -*-
import json
from datetime import datetime
import uuid
import config
import azure.cosmos.cosmos_client as cosmos_client
from flask import request
from flask import Flask
from psycopg2 import connect



def is_target(log, **kwargs):
    return 'Уточнение заказа' in log

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
        print('!!! Error in parse_product_info func !!!')
        load_to_pg(json_txt, 'parse_product_info')

def parse_customer_info(json_txt, **kwargs):
    try:
        return json_txt['callback_query']['from']
    except:
        print('!!! Error in parse_customer_info func !!!')
        load_to_pg(json_txt, 'parse_customer_info')

def parse_date_info(json_txt, **kwargs):
    try:
        return datetime.fromtimestamp(int(json_txt['callback_query']['message']['date'])).strftime('%d-%m-%Y %H:%M:%S')
    except:
        print('!!! Error in parse_date_info func !!!')
        load_to_pg(json_txt, 'parse_date_info')

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
        print('!!! Error in parse_delivery_info func !!!')
        load_to_pg(json_txt, 'parse_delivery_info')

def parse_bill_type_info(json_txt, **kwargs):
    try:
        target_text = json_txt['callback_query']['message']['text']
        block_list = target_text.split("●")
        for block in block_list:
            if "Способ оплаты:" in block and "Итого:" not in block:
                tmp = block.replace("Способ оплаты:", "").replace('\n','').strip()
        return tmp
    except:
        print('!!! Error in parse_bill_type_info func !!!')
        load_to_pg(json_txt, 'parse_bill_type_info')

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
        print('!!! Error in parse_results_info func !!!')
        load_to_pg(json_txt, 'parse_results_info')

def load_to_cosmos(data, **kwargs):
    try:
        HOST = config.cosmos_settings['host']
        MASTER_KEY = config.cosmos_settings['master_key']
        DATABASE_ID = config.cosmos_settings['database_id']
        CONTAINER_ID = config.cosmos_settings['container_id']

        client = cosmos_client.CosmosClient(HOST, {'masterKey': MASTER_KEY})
        db = client.get_database_client(DATABASE_ID)
        container = db.get_container_client(CONTAINER_ID)
        container.create_item(body=data)
    except:
        print('!!! Error in load_to_cosmos func !!!')
        load_to_pg(data, 'load_to_cosmos')

def load_to_pg(data, func, **kwargs):
    db_host = config.pg_settings['db_host']
    db_user = config.pg_settings['db_user']
    db_pass = config.pg_settings['db_pass']
    db_port = config.pg_settings['db_port']
    db_name = config.pg_settings['db_name']

    conn = connect(host=db_host, dbname=db_name, user=db_user, password=db_pass, port=db_port)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(f"insert into service.log (data, func) values('{data}', '{func}')")
    except:
        print('!!! Error in load_to_pg func !!!')
    finally:
        conn.close()

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
            print('!!! Error in main_process func !!!')
            load_to_pg(log, 'main_process')
    else:
        pass

app = Flask(__name__)

@app.route('/', methods = ["POST", "GET"])
def main():
    if request.method == "POST":
        main_process(str(request.json).replace("'", "\""))
        return {"ok": True}
    else:
        return "Hello from grigoryBzr"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=443)