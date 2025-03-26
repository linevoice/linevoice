from flask import Flask, request, jsonify, send_file
from fpdf import FPDF
import os
from datetime import datetime

app = Flask(__name__)

# 保存先ディレクトリ
OUTPUT_DIR = "invoices"
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return "API が動作しています！"

@app.route("/invoice", methods=["POST"])
def create_invoice():
    try:
        # JSON データを取得
        data = request.get_json()
        print("受信データ:", data)  # デバッグ用

        if not data or "宛名" not in data or "金額" not in data or "但し書き" not in data:
            return jsonify({"error": "必要な情報が不足しています"}), 400

        recipient = data["宛名"]
        amount = data["金額"]
        description = data["但し書き"]

        # ファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"invoice_{timestamp}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # PDF を作成
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, "請求書", ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, f"宛名: {recipient}", ln=True)
        pdf.cell(200, 10, f"金額: ¥{amount}", ln=True)
        pdf.cell(200, 10, f"但し書き: {description}", ln=True)
        pdf.output(filepath)

        return send_file(filepath, as_attachment=True)

    except Exception as e:
        print("エラー:", str(e))  # デバッグ用
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)