import requests
from datetime import datetime, timedelta
import myClass


BASE_URL = "https://api-seller.ozon.ru"

def get_products_order(order_data):
    products = []
    for i in range(len(order_data["products"])):
        # for product in order_data["financial_data"]["products"]:
        product_mc = mc.get_product_data(order_data["products"][i]["offer_id"])
        products.append({
            "id_mc": product_mc["id"],
            "id_oz": order_data["products"][i]["sku"],
            "sku": order_data["products"][i]["offer_id"],
            "name": order_data["products"][i]["name"],
            "quantity": order_data["products"][i]["quantity"],
            # "reserve": product["quantity"],
            "price": float(order_data["products"][i]["price"]) * 100,
            "payout": round(float(order_data["financial_data"]["products"][i]["payout"]) * 100, 2),
            "assortment": {"meta": product_mc["meta"]}
        })
        i += 1
    return products


def update_stock(headers, data):
    requests.post(f"{BASE_URL}/v2/products/stocks", headers=headers, data=data)


def update_price(headers, data):
    requests.post(f"{BASE_URL}/v1/product/import/prices", headers=headers, data=data)


# Получить все артикулы товаров в Озон
def get_products_sku(headers):
    data = json.dumps(
        {
            "filter": {
                "visibility": "ALL"
            },
            "last_id": "",
            "limit": 1000
        }
    )
    response = requests.post(f"{BASE_URL}/v3/product/info/stocks", headers=headers, data=data).json()
    sku_list = []
    for item in response["result"]["items"]:
        sku_list.append(item["offer_id"])
    return sku_list


# Получить id всех действующих складов FBS
def get_warehouse_id(headers):
    response = requests.post(f"{BASE_URL}/v1/warehouse/list", headers=headers).json()
    warehouse_list_id = []
    for item in response["result"]:
        if item["status"] == "disabled":
            continue
        else:
            warehouse_list_id.append(item["warehouse_id"])
    return warehouse_list_id


# Получить новые заказы Озон (статус awaiting_packaging)
def get_orders(headers, days, status):
    data = json.dumps(
        {
            "dir": "ASC",
            "filter": {
                "since": f"{datetime.today() - timedelta(days=days, hours=0, minutes=0):%Y-%m-%dT%H:%M:%SZ}",
                "to": f"{datetime.today():%Y-%m-%dT%H:%M:%SZ}",
                "status": status
            },
            "limit": 1000,
            "offset": 0,
            "translit": True,
            "with": {
                "analytics_data": True,
                "financial_data": True
            }
        }
    )
    response = requests.post(f"{BASE_URL}/v3/posting/fbs/list", headers=headers[1], data=data).json()
    orders = []
    order = myClass.Order()
    for item in response["result"]["postings"]:
        order.get_oz_order(item)
        order.shop = headers[0]
        orders.append(order)
    return orders


def get_order(headers, order_number):
    data = json.dumps(
        {
            "posting_number": order_number,
            "with": {
                "analytics_data": True,
                "barcodes": False,
                "financial_data": True,
                "product_exemplars": False,
                "translit": True
            }
        }
    )
    response = requests.post(f"{BASE_URL}/v3/posting/fbs/get", headers=headers[1], data=data).json()
    order = myClass.Order()
    order.get_oz_order(response["result"])
    order.shop = headers[0]
    return order


# Собрать заказ
def collect_order(headers, order):
    data = json.dumps(
        {
            "packages": [
                {
                    "products": order.products
                }
            ],
            "posting_number": order.number,
            "with": {
                "additional_data": True
            }
        }
    )
    requests.post(f"{BASE_URL}/v4/posting/fbs/ship", headers=headers, data=data)


# Скачать этикетку
def get_label(headers, order):
    data = json.dumps(
        {
            "posting_number": [order.number]
        }
    )
    response = requests.post(f"{BASE_URL}/v2/posting/fbs/package-label", headers=headers, data=data)
    # file = open(f"/Users/kosenkov/Library/Mobile Documents/com~apple~CloudDocs/Print/{order_number}.pdf", "wb")
    file = open(f"{login.linux_url}/Yandex.Disk/Print/{order.number}", "wb")
    file.write(response.content)
    file.close()

    # Печать на принтере
    # os.system(f"lpr -P TSC_TE310 {order_number}.pdf")


# Получить возвраты
def get_returns(headers, days, status):
    data = json.dumps(
        {
            "filter": {
                "accepted_from_customer_moment": {
                    "time_from": f"{datetime.today() - timedelta(days=days, hours=0, minutes=0):%Y-%m-%dT%H:%M:%SZ}",
                    "time_to": f"{datetime.today():%Y-%m-%dT%H:%M:%SZ}"
                },
                "status": status
            },
            "limit": 1000,
            "last_id": 0
        }
    )
    return requests.post(f"{BASE_URL}/v3/returns/company/fbs", headers=headers, data=data).json()


def get_finance(headers):
    data = json.dumps(
        {
            "filter": {
                "date": {
                    "from": f"{datetime.today() - timedelta(days=17, hours=0, minutes=0):%Y-%m-%dT%H:%M:%SZ}",
                    "to": f"{datetime.today():%Y-%m-%dT%H:%M:%SZ}",
                },
                "operation_type": [],
                "posting_number": "",
                "transaction_type": "orders"
            },
            "page": 1,
            "page_size": 1000
        }
    )
    return requests.post(f"{BASE_URL}/v3/finance/transaction/list", headers=headers, data=data).json()
