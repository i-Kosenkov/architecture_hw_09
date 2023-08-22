import json
from flask import Flask, request

app = Flask(__name__)


@app.route("/webhook/mc/demand_create", methods=["POST"])
def mc_demand_created():
    response = request.json
    model.update_oz_stock_after_mc_shipment(response["events"][0]["meta"]["href"])
    time.sleep(30)
    model.get_cdek_label_from_mc_demand(response["events"][0]["meta"]["href"])
    return "success", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005, debug=True)
