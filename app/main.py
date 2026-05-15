from fastapi import FastAPI, Request
import os

print("MAIN.PY LOADED")

app = FastAPI()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


# -------- ROOT TEST --------
@app.get("/")
def root():
    return {"status": "running"}


# -------- TELEGRAM WEBHOOK --------
@app.post("/telegram")
async def telegram_webhook(request: Request):
    data = await request.json()

    print("UPDATE RECEIVED:", data)

    # Eksempel: simple command parsing
    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": True}

    response_text = None

    if text == "/start":
        response_text = "🏃 Marathon Coach aktiv"
    elif text == "/status":
        response_text = "CTL: 48 | ATL: 55 | TSB: -7"
    elif text == "/today":
        response_text = "Dagens træning kommer snart 🚀"
    else:
        response_text = "Ukendt kommando. Prøv /start, /status, /today"

    # Send svar tilbage til Telegram
    import requests

    requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": response_text
        }
    )

    return {"ok": True}
    
from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
def root():
    return {"status": "running"}


# STRAVA VERIFICATION (GET + POST SAFE)
@app.api_route("/strava-webhook", methods=["GET", "POST"])
async def strava_webhook(request: Request):

    # GET TEST (Strava validation / browser test)
    if request.method == "GET":
        return {"status": "ok"}

    # POST (actual events)
    data = await request.json()

    print("STRAVA EVENT:", data)

    # IMPORTANT: Strava challenge
    if "hub.challenge" in data:
        return {"hub.challenge": data["hub.challenge"]}

    return {"ok": True}
    
