from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fpdf import FPDF
import uvicorn
import os

app = FastAPI()

# 入力データのスキーマ
class InvoiceRequest(BaseModel):
    recipient: str  # 宛名
    amount: float  # 金額
    description: str  # 但し書き
    tax_type: str  # 税率タイプ（"内税10%", "内税8%", "外税10%", "外税8%"）

# PDF作成関数
def generate_invoice(data: InvoiceRequest):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)  # フォント変更（Arial → Helvetica）

    # ヘッダー
    pdf.cell(200, 10, txt="請求書", ln=True, align="C")

    # 宛名
    pdf.cell(200, 10, txt=f"宛名: {data.recipient}", ln=True, align="L")

    # 金額計算
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
        amount_ex_tax = data.amount / (1 + tax_rate)  # 内税の税抜き計算
        tax_amount = data.amount - amount_ex_tax
        total_amount = data.amount
    else:
        tax_amount = data.amount * tax_rate  # 外税の税額計算
        total_amount = data.amount + tax_amount

    # 金額詳細
    pdf.cell(200, 10, txt=f"金額: {amount_ex_tax:.2f} 円", ln=True, align="L")
    pdf.cell(200, 10, txt=f"消費税 ({data.tax_type}): {tax_amount:.2f} 円", ln=True, align="L")
    pdf.cell(200, 10, txt=f"合計金額: {total_amount:.2f} 円", ln=True, align="L")

    # 但し書き
    pdf.cell(200, 10, txt=f"但し書き: {data.description}", ln=True, align="L")

    # 一時フォルダ `/tmp/` に保存（Renderで安定して動作するように）
    file_path = "/tmp/invoice.pdf"
    pdf.output(file_path)
    return file_path

# APIエンドポイント（PDFをダウンロード可能にする）
@app.post("/generate_invoice/")
async def generate_invoice_endpoint(request: InvoiceRequest):
    file_path = generate_invoice(request)
    return FileResponse(path=file_path, filename="invoice.pdf", media_type="application/pdf")

# Uvicornで起動
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
