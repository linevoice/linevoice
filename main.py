from flask import Flask, request, jsonify, send_file
import json
from invoice import generate_invoice
import os
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "サクッと請求 API が動作しています。"}), 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logging.debug(f"Received data: {data}")

        message = data.get("events", [{}])[0].get("message", {})
        message_text = message.get("text", "")

        if not message_text:
            return jsonify({"error": "No text found in message"}), 400

        invoice_data = json.loads(message_text)
        logging.debug(f"Parsed invoice data: {invoice_data}")

        pdf_path = generate_invoice(invoice_data)
        logging.debug(f"Generated PDF path: {pdf_path}")

        return jsonify({"pdf_url": pdf_path})

    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON format"}), 400

    except Exception as e:
        logging.error(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/invoice/<filename>", methods=["GET"])
def get_invoice(filename):
    """作成された請求書 PDF を取得するエンドポイント"""
    pdf_path = os.path.join("invoices", filename)
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True)
    return jsonify({"error": "File not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # デフォルト 10000 に設定
    app.run(host="0.0.0.0", port=port, debug=True)