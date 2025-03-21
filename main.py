from fastapi import FastAPI, Request
import json
from invoice import create_invoice

app = FastAPI()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print("Received webhook:", body)

    for event in body.get("events", []):
        if event["type"] == "message" and event["message"]["type"] == "text":
            text = event["message"]["text"]
            parts = text.split("\n")
            if len(parts) >= 3:
                name, amount, description = parts[:3]
                pdf_filename = create_invoice(name, amount, description)
                print(f"作成した請求書: {pdf_filename}")
    
    return {"message": "Webhook received!"}
