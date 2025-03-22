from fpdf import FPDF

class InvoicePDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, "請求書", ln=True, align="C")

    def add_invoice_details(self, invoice_data):
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"宛名: {invoice_data['宛名']}", ln=True)
        self.cell(0, 10, f"発行日: {invoice_data['発行日']}", ln=True)
        self.cell(0, 10, f"税率: {invoice_data['税率']}", ln=True)
        self.ln(10)

    def add_invoice_items(self, items):
        self.set_font("Arial", "B", 10)
        self.cell(50, 10, "品目", border=1)
        self.cell(30, 10, "単価", border=1)
        self.cell(30, 10, "数量", border=1)
        self.cell(30, 10, "小計", border=1)
        self.ln()

        self.set_font("Arial", "", 10)
        for item in items:
            self.cell(50, 10, item["品目"], border=1)
            self.cell(30, 10, str(item["単価"]), border=1)
            self.cell(30, 10, str(item["数量"]), border=1)
            self.cell(30, 10, str(item["小計"]), border=1)
            self.ln()

    def add_total(self, total, tax, grand_total):
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, f"合計金額: {total} 円", ln=True)
        self.cell(0, 10, f"消費税: {tax} 円", ln=True)
        self.cell(0, 10, f"総額: {grand_total} 円", ln=True)

def generate_invoice(invoice_data):
    pdf = InvoicePDF()
    pdf.add_page()
    pdf.add_invoice_details(invoice_data)
    pdf.add_invoice_items(invoice_data["内訳"])
    
    total = sum(item["小計"] for item in invoice_data["内訳"])
    tax = int(total * 0.1)  # 10% 消費税
    grand_total = total + tax

    pdf.add_total(total, tax, grand_total)

    file_path = "invoice.pdf"
    pdf.output(file_path)
    return file_path