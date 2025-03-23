from flask import Flask, request, jsonify
from fpdf import FPDF
import os

app = Flask(__name__)

SAVE_FOLDER = "invoices"
os.makedirs(SAVE_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return "API が動作しています！"

@app.route("/invoice", methods=["POST"])
def create_invoice():
    """
    請求書を生成するエンドポイント
    """
    data = request.json
    if not data or "宛名" not in data or "金額" not in data or "但し書き" not in data:
        return jsonify({"error": "不正なリクエスト"}), 400

    customer_name = data["宛名"]
    amount = data["金額"]
    description = data["但し書き"]

    invoice_id = len(os.listdir(SAVE_FOLDER)) + 1
    pdf_filename = f"{SAVE_FOLDER}/invoice_{invoice_id}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=16)
    pdf.cell(200, 10, txt="請求書", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"宛名: {customer_name}", ln=True)
    pdf.cell(200, 10, txt=f"金額: ¥{amount}", ln=True)
    pdf.cell(200, 10, txt=f"但し書き: {description}", ln=True)

    pdf.output(pdf_filename)

    return jsonify({
        "status": "success",
        "message": "請求書が作成されました。",
        "invoice_url": f"https://your-service.onrender.com/{pdf_filename}"
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)