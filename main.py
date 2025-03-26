from flask import Flask, request, jsonify, send_file
from fpdf import FPDF
import os
from datetime import datetime

app = Flask(__name__)

# 保存先ディレクトリ
OUTPUT_DIR = "invoices"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def utf8_to_latin1(text):
    """UTF-8 文字列を latin-1 に変換（変換できない文字は無視）"""
    return text.encode("utf-8").decode("latin-1", "ignore")

@app.route("/", methods=["GET"])
def home():
    return "API が動作しています！"

@app.route("/invoice", methods=["POST"])
def create_invoice():
    try:
        # JSON データを取得（エンコーディングの問題を回避）
        data = request.get_json(force=True)
        if not data:
            return jsonify({"error": "リクエストボディが空です。JSONデータを送信してください。"}), 400

        recipient = data.get("宛名", "不明")
        amount = data.get("金額", "0")
        description = data.get("但し書き", "記載なし")

        # ファイル名を生成
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"invoice_{timestamp}.pdf"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # PDF を作成
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.cell(200, 10, utf8_to_latin1("請求書"), ln=True, align="C")
        pdf.ln(10)
        pdf.cell(200, 10, utf8_to_latin1(f"宛名: {recipient}"), ln=True)
        pdf.cell(200, 10, utf8_to_latin1(f"金額: ¥{amount}"), ln=True)
        pdf.cell(200, 10, utf8_to_latin1(f"但し書き: {description}"), ln=True)
        pdf.output(filepath, "F")  # ファイルに保存

        return send_file(filepath, as_attachment=True, download_name="invoice.pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)