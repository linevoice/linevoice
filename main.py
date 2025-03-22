from flask import Flask, request, send_file
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os
import invoice
import utils

app = Flask(__name__)

# 環境変数からLINEの設定を取得
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

@app.route("/webhook", methods=["POST"])
def webhook():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        return "Invalid signature", 400

    return "OK", 200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text
    data = utils.parse_message(text)

    if not data:
        reply_text = "請求書を作成するには、以下の形式で送信してください。\n\n"
        reply_text += "宛名: 株式会社〇〇\n金額: 10000\n但書: サービス料金\n発行日: 2025-03-21\n税率: 内税10%"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))
        return

    pdf_path = invoice.create_invoice(data)
    pdf_url = utils.upload_to_storage(pdf_path)

    reply_text = f"請求書を作成しました。\n📄 {pdf_url}"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

if __name__ == "__main__":
    app.run(debug=True)