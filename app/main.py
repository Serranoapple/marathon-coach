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
import os
import requests

app = FastAPI()

STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")


@app.get("/")
def root():
    return {"status": "running"}


@app.api_route("/strava-webhook", methods=["GET", "POST"])
async def strava_webhook(request: Request):

    # -----------------------------------
    # STRAVA VERIFICATION
    # -----------------------------------
    if request.method == "GET":
        params = dict(request.query_params)

        if "hub.challenge" in params:
            return {
                "hub.challenge": params["hub.challenge"]
            }

        return {"status": "ok"}

    # -----------------------------------
    # STRAVA EVENTS
    # -----------------------------------
    data = await request.json()

    print("STRAVA EVENT:", data)

    # kun nye aktiviteter
    if (
        data.get("object_type") == "activity"
        and data.get("aspect_type") == "create"
    ):

        activity_id = data.get("object_id")

        print("NEW ACTIVITY:", activity_id)

        # hent activity details
        headers = {
            "Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"
        }

        response = requests.get(
            f"https://www.strava.com/api/v3/activities/{activity_id}",
            headers=headers
        )

        activity = response.json()

        print("ACTIVITY DATA:", activity)

    return {"ok": True}
    

