import os
from flask import Flask, request, jsonify
import requests
from dotenv import load_dotenv
from threading import Thread

load_dotenv()
app = Flask(__name__)

# 环境变量
LARK_APP_TOKEN = os.getenv("LARK_APP_TOKEN")
LARK_USER_ID = os.getenv("LARK_USER_ID")
ZOHO_ACCESS_TOKEN = os.getenv("ZOHO_ACCESS_TOKEN")
ZOHO_ORGANIZATION_ID = os.getenv("ZOHO_ORGANIZATION_ID")


@app.route('/zoho-sales-order', methods=['POST'])
def zoho_sales_order():
    data = request.json
    print("📦 Received Zoho Sales Order:", data)

    sales_order = data.get("salesorder", {})
    sales_order_id = sales_order.get("salesorder_id")
    customer_name = sales_order.get("customer_name")
    total = sales_order.get("total")

    # 构造审批请求数据
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

    # 向飞书发起审批
    try:
        response = requests.post(
            "https://open.larksuite.com/open-apis/approval/v4/instances",
            headers=headers,
            json=lark_payload
        )
        print("📤 Lark Approval Sent:", response.json())
        return jsonify({"status": "Lark approval sent"}), 200
    except Exception as e:
        print("❌ Error sending to Lark:", e)
        return jsonify({"error": str(e)}), 500


@app.route('/lark-callback', methods=['POST'])
def lark_callback():
    data = request.json
    print("📥 Lark callback received:", data)

    # 1. 飞书 URL 校验请求
    if data.get("type") == "url_verification":
        return jsonify({"challenge": data.get("challenge")})

    # 启动后台线程异步处理，避免超时
    Thread(target=process_lark_data, args=(data,)).start()

    # 立即响应，避免超时
    return jsonify({"code": 0, "msg": "OK"}), 200


def process_lark_data(data):
    try:
        form = data.get("form", {})
        approval_result = data.get("approval_result")
        sales_order_id = form.get("Sales Order ID")

        # 更新 Zoho 销售订单
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

        res = requests.put(zoho_url, headers=headers, json=update_data)
        print("✅ Zoho Sales Order updated:", res.json())
    except Exception as e:
        print("❌ Error updating Zoho:", e)
