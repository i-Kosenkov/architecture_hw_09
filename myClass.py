import ozon


class Order:
    def __init__(self):
        self.number = ""
        self.id = ""
        self.organization = mc.organization[1]  # Организация ИП
        self.organization_account = mc.organization_account[1]  # Счет эквайринг
        self.shop = ""
        self.counterparty = mc.counterparty[0]  # Розничный покупатель
        self.customer_name = ""
        self.customer_phone = ""
        self.customer_email = ""
        self.customer_company = ""
        self.customer_inn = ""
        self.comment = ""
        self.products = ""
        self.delivery = ""
        self.delivery_address = ""
        self.delivery_point = ""
        self.delivery_price = ""
        self.track_number = ""
        self.delivering_date = ""
        self.status = ""
        self.status_mc = ""
        self.status_delivery = ""
        self.payment_system = ""
        self.has_invoice = False

    def get_oz_order(self, order_data):
        self.payment_system = "market"
        self.number = order_data["posting_number"]
        self.organization_account = mc.organization_account[0]
        self.counterparty = mc.counterparty[1]  # Интернет решения
        self.status = order_data["status"]
        self.delivery = order_data["analytics_data"]["delivery_type"]
        self.delivery_address = order_data["analytics_data"]["city"]
        self.delivering_date = order_data["delivering_date"]
        self.products = ozon.get_products_order(order_data)

    def get_tilda_order(self, order_data):
        self.number = order_data["payment"]["orderid"]
        self.shop = order_data["store"]
        self.customer_name = order_data["name"]
        self.customer_phone = order_data["phone"]
        self.customer_email = order_data["email"]
        self.payment_system = order_data["paymentsystem"]

        if self.payment_system != "sberbank":
            self.organization_account = mc.organization_account[0]
            try:
                self.customer_inn = order_data["inn"]
                # Ищем контрагента в МС по ИНН
                counterparty = mc.get_counterparty(self.customer_inn)
                if counterparty:
                    self.counterparty = counterparty
                    self.has_invoice = True
            except Exception as err:
                logger.exception(err)

        try:
            self.customer_company = order_data["companyname"]
        except Exception as err:
            logger.exception(err)

        try:
            self.comment = order_data["comment"]
        except Exception as err:
            logger.exception(err)

        self.delivery = order_data["payment"]["delivery"]
        self.delivery_address = order_data["payment"]["delivery_address"]
        self.delivery_price = order_data["payment"]["delivery_price"]
        self.comment = self.delivery + "\n" + self.comment
        self.products = tilda.get_products_order(order_data)


class Product:
    def __init__(self):
        self.meta = ""
        self.sku = ""
        self.id = ""
        self.external_code = ""
        self.name = ""
        self.stock = ""
        self.reserve = ""
        self.quantity = ""
        self.price = ""
