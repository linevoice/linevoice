from fpdf import FPDF
import datetime

def create_invoice(name, amount, description):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="請求書", ln=True, align="C")
    pdf.ln(10)
    
    date = datetime.date.today().strftime("%Y-%m-%d")
    pdf.cell(200, 10, txt=f"発行日: {date}", ln=True, align="R")
    pdf.ln(10)

    pdf.cell(200, 10, txt=f"宛名: {name}", ln=True)
    pdf.cell(200, 10, txt=f"金額: ¥{amount}", ln=True)
    pdf.cell(200, 10, txt=f"但し書き: {description}", ln=True)

    filename = f"invoice_{name}_{date}.pdf"
    pdf.output(filename)
    return filename
