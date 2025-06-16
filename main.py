from flask import Flask, request, jsonify
import hashlib
import hmac
import base64
import datetime
import requests

app = Flask(__name__)

# 쿠팡 API 설정
VENDOR_ID = "A01348664"
ACCESS_KEY = "39e7629c-6405-464d-a62e-908718974589"
SECRET_KEY = "944a97f3e38b4577e3fa00895605f098a64de355"
COUPANG_BASE_URL = "https://api-gateway.coupang.com"

@app.route("/")
def home():
    return jsonify({"status": "ok", "message": "Coupang Order Proxy is running"})

@app.route("/orders", methods=["GET"])
def get_orders():
    created_at_from = request.args.get("createdAtFrom")
    created_at_to = request.args.get("createdAtTo")

    if not created_at_from or not created_at_to:
        return jsonify({"error": "Missing required date parameters"}), 400

    path = f"/v2/providers/openapi/apis/api/v4/vendors/{VENDOR_ID}/ordersheets"
    query = f"createdAtFrom={created_at_from}&createdAtTo={created_at_to}"
    url = f"{COUPANG_BASE_URL}{path}?{query}"

    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S')
    message = f"{timestamp}GET{path}"
    signature = base64.b64encode(hmac.new(
        SECRET_KEY.encode('utf-8'),
        message.encode('utf-8'),
        digestmod=hashlib.sha256
    ).digest()).decode()

    authorization = f"HMAC-SHA256 algorithm=HmacSHA256, access-key={ACCESS_KEY}, signed-date={timestamp}, signature={signature}"

    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json",
        "X-Requested-By": "minerva_api",
        "Date": timestamp
    }

    response = requests.get(url, headers=headers)
    return jsonify(response.json()), response.status_code

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
