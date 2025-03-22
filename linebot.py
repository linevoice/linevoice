from flask import Flask, request, send_file
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
from invoice import InvoiceGenerator
import datetime

app = Flask(__name__)

# LINE Bot API設定
LINE_CHANNEL_ACCESS_TOKEN = "あなたのアクセストークン"
LINE_CHANNEL_SECRET = "あなたのシークレット"
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 会社情報（事前登録）
COMPANY_NAME = "あなたの会社名"
COMPANY_ADDRESS = "あなたの会社の住所"
BANK_INFO = "銀行口座情報"
LOGO_PATH = "logo.png"  # 事前登録したロゴ
STAMP_PATH = "stamp.png"  # 事前登録した印影

invoice_generator = InvoiceGenerator(COMPANY_NAME, COMPANY_ADDRESS, BANK_INFO, LOGO_PATH, STAMP_PATH)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    
    # 入力フォーマット（宛名, 金額, 但書, 発行日, 税率）
    try:
        recipient, amount, description, issue_date, tax_rate = map(str.strip, text.split(","))
        amount = int(amount.replace("¥", "").replace(",", ""))
    except ValueError:
        reply_text = "入力形式が正しくありません。\n「宛名, 金額, 但書, 発行日, 税率」の順で入力してください。"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return

    # PDF生成
    pdf_path = f"invoice_{event.source.user_id}.pdf"
    invoice_generator.generate_invoice(recipient, amount, description, issue_date, tax_rate, pdf_path)

    # PDFを送信
    line_bot_api.reply_message(
        event.reply_token,
        [
            TextSendMessage(text="請求書を作成しました。以下のリンクからダウンロードしてください。"),
            TextSendMessage(text=f"{request.url_root}download/{pdf_path}")
        ]
    )

@app.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)