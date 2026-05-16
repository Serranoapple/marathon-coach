from fastapi import FastAPI, Request
import os
import requests
from supabase import create_client

print("MAIN.PY LOADED")

app = FastAPI()

# -----------------------------------
# ENV VARIABLES
# -----------------------------------

STRAVA_ACCESS_TOKEN = os.getenv("STRAVA_ACCESS_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# -----------------------------------
# SUPABASE CLIENT
# -----------------------------------

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# -----------------------------------
# ROOT TEST
# -----------------------------------

@app.get("/")
def root():
    return {"status": "running"}

# -----------------------------------
# TELEGRAM WEBHOOK
# -----------------------------------

@app.post("/telegram")
async def telegram_webhook(request: Request):

    data = await request.json()

    print("TELEGRAM EVENT:", data)

    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": True}

    response_text = None

    if text == "/start":

        response_text = (
            "🏃 Marathon Coach aktiv\n\n"
            "Kommandoer:\n"
            "/status\n"
            "/today"
        )

    elif text == "/status":

        response_text = (
            "📊 System status\n\n"
            "Webhook: OK\n"
            "Strava: Connected\n"
            "Database: Connected"
        )

    elif text == "/today":

        response_text = (
            "🏃 Dagens forslag\n\n"
            "30 min roligt Zone 2 løb"
        )

    else:

        response_text = (
            "Ukendt kommando.\n\n"
            "Prøv:\n"
            "/start\n"
            "/status\n"
            "/today"
        )

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": response_text
        }
    )

    return {"ok": True}

# -----------------------------------
# STRAVA WEBHOOK
# -----------------------------------

@app.api_route("/strava-webhook", methods=["GET", "POST"])
async def strava_webhook(request: Request):

    print("=== STRAVA REQUEST ===")
    print("METHOD:", request.method)

    # -----------------------------------
    # STRAVA VERIFICATION
    # -----------------------------------

    if request.method == "GET":

        params = dict(request.query_params)

        print("QUERY PARAMS:", params)

        if "hub.challenge" in params:

            print("CHALLENGE RECEIVED")

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

        print("NEW ACTIVITY ID:", activity_id)

        headers = {
            "Authorization": f"Bearer {STRAVA_ACCESS_TOKEN}"
        }

        response = requests.get(
            f"https://www.strava.com/api/v3/activities/{activity_id}",
            headers=headers
        )

        print("STRAVA API STATUS:", response.status_code)

        activity = response.json()

        print("ACTIVITY DATA:", activity)

        # -----------------------------------
        # KUN LØB
        # -----------------------------------

        if activity.get("type") == "Run":

            name = activity.get("name")

            distance_km = round(
                activity.get("distance", 0) / 1000,
                2
            )

            moving_time = activity.get("moving_time", 0)

            if distance_km > 0:

                pace_seconds = moving_time / distance_km

                minutes = int(pace_seconds // 60)
                seconds = int(pace_seconds % 60)

                pace = f"{minutes}:{seconds:02d}/km"

            else:

                pace = "N/A"

            average_hr = activity.get("average_heartrate")

            print("=== RUN DETECTED ===")
            print("NAME:", name)
            print("DISTANCE:", distance_km)
            print("PACE:", pace)
            print("AVG HR:", average_hr)

            # -----------------------------------
            # SAVE TO SUPABASE
            # -----------------------------------

            try:

                supabase.table("runs").insert({
                    "id": activity_id,
                    "name": name,
                    "distance_km": distance_km,
                    "moving_time": moving_time,
                    "pace": pace,
                    "average_hr": average_hr
                }).execute()

                print("RUN SAVED TO DATABASE")

            except Exception as e:

                print("DATABASE ERROR:", e)

            # -----------------------------------
            # TELEGRAM FEEDBACK
            # -----------------------------------

            feedback = (
                f"🏃 Ny løbetur registreret\n\n"
                f"Navn: {name}\n"
                f"Distance: {distance_km} km\n"
                f"Pace: {pace}\n"
                f"Puls: {average_hr}"
            )

            # INDSÆT DIT TELEGRAM CHAT ID HER
            TELEGRAM_CHAT_ID = "DIT_CHAT_ID"

            try:

                requests.post(
                    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                    json={
                        "chat_id": TELEGRAM_CHAT_ID,
                        "text": feedback
                    }
                )

                print("TELEGRAM MESSAGE SENT")

            except Exception as e:

                print("TELEGRAM ERROR:", e)

    return {"ok": True}
