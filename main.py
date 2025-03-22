from flask import Flask, request, jsonify
import json
from invoice import generate_invoice

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        # LINE から送られたデータを取得
        data = request.get_json()
        message_text = data["events"][0]["message"]["text"]

        # 請求データを JSON で送る前提
        invoice_data = json.loads(message_text)

        # PDF を作成
        pdf_path = generate_invoice(invoice_data)

        return jsonify({"pdf_url": pdf_path})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # PORT がなければデフォルトで 5000
    app.run(host="0.0.0.0", port=port)