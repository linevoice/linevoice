from fpdf import FPDF
import datetime

class InvoiceGenerator:
    def __init__(self, company_name, company_address, bank_info, logo_path=None, stamp_path=None):
        self.company_name = company_name
        self.company_address = company_address
        self.bank_info = bank_info
        self.logo_path = logo_path
        self.stamp_path = stamp_path

    def generate_invoice(self, recipient, amount, description, issue_date, tax_rate, output_path="invoice.pdf"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "", 12)

        # 会社ロゴ
        if self.logo_path:
            pdf.image(self.logo_path, 10, 10, 30)

        # タイトル
        pdf.set_xy(80, 10)
        pdf.set_font("Arial", "B", 16)
        pdf.cell(50, 10, "請求書", ln=True, align="C")

        # 会社情報
        pdf.set_xy(10, 30)
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 7, f"{self.company_name}\n{self.company_address}\n{self.bank_info}")

        # 宛名
        pdf.set_xy(10, 60)
        pdf.cell(0, 10, f"請求先: {recipient}", ln=True)

        # 発行日
        pdf.cell(0, 10, f"発行日: {issue_date}", ln=True)

        # 金額
        tax_multiplier = 1 if "内税" in tax_rate else (1 + int(tax_rate[-2:]) / 100)
        tax_amount = amount - (amount / tax_multiplier)
        pdf.cell(0, 10, f"請求額: ¥{amount:,.0f}（税額 ¥{tax_amount:,.0f}）", ln=True)

        # 但書
        pdf.cell(0, 10, f"但し: {description}", ln=True)

        # 訂正不可
        pdf.set_font("Arial", "B", 10)
        pdf.set_xy(10, 120)
        pdf.cell(0, 10, "※本請求書は訂正不可です。", ln=True)

        # 会社印
        if self.stamp_path:
            pdf.image(self.stamp_path, 160, 80, 30)

        # PDF 保存
        pdf.output(output_path)

        return output_path