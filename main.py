import os
import json
import requests
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from fpdf import FPDF
import uvicorn

from fastapi.responses import FileResponse

app = FastAPI()

LINE_ACCESS_TOKEN = "YOUR_LINE_ACCESS_TOKEN"

class InvoiceRequest(BaseModel):
    recipient: str
    amount: float
    description: str
    tax_type: str

# PDF作成関数（今のまま使う）
def generate_invoice(data: InvoiceRequest):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="請求書", ln=True, align="C")
    pdf.cell(200, 10, txt=f"宛名: {data.recipient}", ln=True, align="L")

    tax_rates = {
        "内税10%": 0.10,
        "内税8%": 0.08,
        "外税10%": 0.10,
        "外税8%": 0.08,
    }

    if data.tax_type not in tax_rates:
        raise HTTPException(status_code=400, detail="無効な税率タイプ")

    tax_rate = tax_rates[data.tax_type]

    if "内税" in data.tax_type:
        amount_ex_tax = data.amount / (1 + tax_rate)
        tax_amount = data.amount - amount_ex_tax
        total_amount = data.amount
    else:
        tax_amount = data.amount * tax_rate
        total_amount = data.amount + tax_amount

    pdf.cell(200, 10, txt=f"金額: {amount_ex_tax:.2f} 円", ln=True, align="L")
    pdf.cell(200, 10, txt=f"消費税 ({data.tax_type}): {tax_amount:.2f} 円", ln=True, align="L")
    pdf.cell(200, 10, txt=f"合計金額: {total_amount:.2f} 円", ln=True, align="L")
    pdf.cell(200, 10, txt=f"但し書き: {data.description}", ln=True, align="L")

    file_path = "invoice.pdf"
    pdf.output(file_path)
    return file_path

@app.post("/generate_invoice/")
async def generate_invoice_endpoint(request: InvoiceRequest):
    file_path = generate_invoice(request)
    return FileResponse(file_path, media_type="application/pdf", filename="invoice.pdf")

# ✅ LINEのWebhookを追加
@app.post("/webhook")
async def line_webhook(request: Request):
    body = await request.body()
    data = json.loads(body.decode("utf-8"))

    for event in data.get("events", []):
        if event["type"] == "message" and "text" in event["message"]:
            user_id = event["source"]["userId"]
            text = event["message"]["text"]

            # ✅ ユーザーのメッセージから請求データを解析（例: "田中太郎, 10000, Web制作, 内税10%"）
            try:
                recipient, amount, description, tax_type = text.split(", ")
                amount = float(amount)
            except ValueError:
                send_line_message(user_id, "入力形式が正しくありません。\n例: 田中太郎, 10000, Web制作, 内税10%")
                continue

            # ✅ PDFを作成
            request_data = InvoiceRequest(
                recipient=recipient,
                amount=amount,
                description=description,
                tax_type=tax_type
            )
            file_path = generate_invoice(request_data)

            # ✅ PDFを送信
            send_line_pdf(user_id, file_path)

    return {"message": "OK"}

# ✅ LINEのメッセージ送信関数
def send_line_message(user_id, text):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    data = {
        "to": user_id,
        "messages": [{"type": "text", "text": text}]
    }
    requests.post(url, headers=headers, json=data)

# ✅ LINEでPDFを送る関数
def send_line_pdf(user_id, file_path):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Authorization": f"Bearer {LINE_ACCESS_TOKEN}"
    }
    files = {
        "file": open(file_path, "rb")
    }
    data = {
        "to": user_id,
        "messages": [{
            "type": "file",
            "fileName": "invoice.pdf",
            "fileSize": os.path.getsize(file_path)
        }]
    }
    requests.post(url, headers=headers, files=files, json=data)

# Uvicornで起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)