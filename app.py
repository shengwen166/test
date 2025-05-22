import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Load environment variables
LARK_APP_TOKEN = os.getenv("LARK_APP_TOKEN")
LARK_USER_ID = os.getenv("LARK_USER_ID")
ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
ZOHO_ORGANIZATION_ID = os.getenv("ZOHO_ORGANIZATION_ID")

@app.route('/zoho-sales-order', methods=['POST'])
def zoho_sales_order():
    data = request.json
    sales_order = data.get("salesorder", {})
    sales_order_id = sales_order.get("salesorder_id")
    customer_name = sales_order.get("customer_name")
    total = sales_order.get("total")

    lark_payload = {
        "approval_code": "SALES_ORDER_APPROVAL",
        "user_id": LARK_USER_ID,
        "form": {
            "title": f"Sales Order - {customer_name}",
            "fields": [
                {"name": "Sales Order ID", "value": sales_order_id},
                {"name": "Customer Name", "value": customer_name},
                {"name": "Total", "value": str(total)}
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {LARK_APP_TOKEN}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        "https://open.larksuite.com/open-apis/approval/v4/instances",
        headers=headers,
        json=lark_payload
    )

    return jsonify({"status": "Lark approval sent", "response": response.json()}), 200

@app.route('/lark-callback', methods=['POST'])
def lark_callback():
    data = request.json
    form = data.get("form", {})
    approval_result = data.get("approval_result")
    sales_order_id = form.get("Sales Order ID")

    zoho_url = f"https://www.zohoapis.com/books/v3/salesorders/{sales_order_id}?organization_id={ZOHO_ORGANIZATION_ID}"
    headers = {
        "Authorization": f"Zoho-oauthtoken {ZOHO_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    update_data = {
        "custom_fields": [
            {"label": "Approval Status", "value": approval_result}
        ]
    }

    zoho_response = requests.put(zoho_url, headers=headers, json=update_data)

    return jsonify({"status": "Zoho updated", "zoho_response": zoho_response.json()}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
