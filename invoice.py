from weasyprint import HTML
import os

def create_invoice(data):
    html_template = f"""
    <html>
    <body>
        <h1>請求書</h1>
        <p><strong>宛名:</strong> {data['name']}</p>
        <p><strong>金額:</strong> {data['amount']} 円</p>
        <p><strong>但書:</strong> {data['description']}</p>
        <p><strong>発行日:</strong> {data['date']}</p>
        <p><strong>税率:</strong> {data['tax_rate']}</p>
    </body>
    </html>
    """
    
    pdf_path = "invoice.pdf"
    HTML(string=html_template).write_pdf(pdf_path)
    return pdf_path