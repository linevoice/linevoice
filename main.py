from fastapi import FastAPI

app = FastAPI()

@app.post("/webhook")
async def webhook(data: dict):
    print("Received webhook:", data)
    return {"message": "Webhook received!"}
