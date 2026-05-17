from fastapi import FastAPI, Request
import os
import requests

from apscheduler.schedulers.background import (
    BackgroundScheduler
)

from supabase import create_client

from app.services.metrics_service import (
    calculate_metrics
)

from app.services.ai_service import (
    generate_coaching_feedback
)

from app.services.prediction_service import (
    predict_marathon
)

from app.services.strava_service import (
    refresh_access_token
)

from app.services.training_plan_service import (
    generate_training_recommendation
)

from app.services.briefing_service import (
    send_daily_briefing
)

from app.services.recovery_service import (
    calculate_recovery_status
)

print("MAIN.PY LOADED")

app = FastAPI()

# -----------------------------------
# ENV VARIABLES
# -----------------------------------

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)

SUPABASE_URL = os.getenv(
    "SUPABASE_URL"
)

SUPABASE_KEY = os.getenv(
    "SUPABASE_KEY"
)

# -----------------------------------
# SUPABASE CLIENT
# -----------------------------------

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# -----------------------------------
# DAILY BRIEFING SCHEDULER
# -----------------------------------

scheduler = BackgroundScheduler()

scheduler.add_job(
    lambda: send_daily_briefing(
        supabase
    ),
    "cron",
    hour=5,
    minute=0
)

scheduler.start()

print("SCHEDULER STARTED")

# -----------------------------------
# ROOT TEST
# -----------------------------------

@app.get("/")
def root():

    return {
        "status": "running"
    }

# -----------------------------------
# TELEGRAM WEBHOOK
# -----------------------------------

@app.post("/telegram")
async def telegram_webhook(
    request: Request
):

    data = await request.json()

    print(
        "TELEGRAM EVENT:",
        data
    )

    message = data.get(
        "message",
        {}
    )

    text = message.get(
        "text",
        ""
    )

    chat_id = (
        message
        .get("chat", {})
        .get("id")
    )

    if not chat_id:

        return {"ok": True}

    response_text = None

    # -----------------------------------
    # COMMANDS
    # -----------------------------------

    if text == "/start":

        response_text = (
            "🏃 Marathon AI Coach aktiv\n\n"
            "Kommandoer:\n"
            "/status\n"
            "/today\n"
            "/weekly\n"
            "/prediction\n"
            "/recovery"
        )

    elif text == "/status":

        metrics = calculate_metrics(
            supabase
        )

        prediction = predict_marathon(
            metrics
        )

        recovery = (
            calculate_recovery_status(
                supabase
            )
        )

        response_text = (
            "📊 System status\n\n"
            f"Ugens km: "
            f"{metrics['weekly_distance']}\n"
            f"Antal løb: "
            f"{metrics['run_count']}\n"
            f"Gns pace: "
            f"{metrics['average_pace']}\n"
            f"Readiness: "
            f"{prediction['readiness_score']}/100\n"
            f"Recovery: "
            f"{recovery['status']}"
        )

        if metrics["fatigue_warning"]:

            response_text += (
                "\n\n⚠ Belastningen er høj."
            )

    elif text == "/today":

        metrics = calculate_metrics(
            supabase
        )

        prediction = predict_marathon(
            metrics
        )

        recommendation = (
            generate_training_recommendation(
                metrics,
                prediction
            )
        )

        recovery = (
            calculate_recovery_status(
                supabase
            )
        )

        response_text = (
            "📅 Dagens anbefaling\n\n"
            f"{recommendation}\n\n"
            f"🩺 Recovery\n"
            f"{recovery['message']}"
        )

    elif text == "/weekly":

        metrics = calculate_metrics(
            supabase
        )

        prediction = predict_marathon(
            metrics
        )

        recommendation = (
            generate_training_recommendation(
                metrics,
                prediction
            )
        )

        recovery = (
            calculate_recovery_status(
                supabase
            )
        )

        response_text = (
            "📈 Weekly Summary\n\n"
            f"Distance: "
            f"{metrics['weekly_distance']} km\n"
            f"Antal løb: "
            f"{metrics['run_count']}\n"
            f"Gns pace: "
            f"{metrics['average_pace']}\n\n"
            f"🩺 Recovery\n"
            f"{recovery['message']}\n\n"
            f"📅 Recommendation\n"
            f"{recommendation}"
        )

        if metrics["fatigue_warning"]:

            response_text += (
                "\n\n⚠ Belastningen er høj."
            )

    elif text == "/prediction":

        metrics = calculate_metrics(
            supabase
        )

        prediction = predict_marathon(
            metrics
        )

        recovery = (
            calculate_recovery_status(
                supabase
            )
        )

        response_text = (
            "🏁 Marathon Prediction\n\n"
            f"Tid: "
            f"{prediction['predicted_time']}\n"
            f"Readiness: "
            f"{prediction['readiness_score']}/100\n"
            f"Sub 4 chance: "
            f"{prediction['sub4_probability']}%\n\n"
            f"🩺 Recovery\n"
            f"{recovery['message']}"
        )

    elif text == "/recovery":

        recovery = (
            calculate_recovery_status(
                supabase
            )
        )

        response_text = (
            "🩺 Recovery Status\n\n"
            f"Acute load: "
            f"{recovery['acute_load']} km\n"
            f"Chronic load: "
            f"{recovery['chronic_load']} km\n"
            f"Ratio: "
            f"{recovery['load_ratio']}\n\n"
            f"{recovery['message']}"
        )

    else:

        response_text = (
            "Ukendt kommando.\n\n"
            "Prøv:\n"
            "/start\n"
            "/status\n"
            "/today\n"
            "/weekly\n"
            "/prediction\n"
            "/recovery"
        )

    # -----------------------------------
    # SEND TELEGRAM MESSAGE
    # -----------------------------------

    try:

        requests.post(
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}/"
            f"sendMessage",
            json={
                "chat_id": chat_id,
                "text": response_text
            }
        )

        print(
            "TELEGRAM RESPONSE SENT"
        )

    except Exception as e:

        print(
            "TELEGRAM ERROR:",
            e
        )

    return {"ok": True}

# -----------------------------------
# STRAVA WEBHOOK
# -----------------------------------

@app.api_route(
    "/strava-webhook",
    methods=["GET", "POST"]
)

async def strava_webhook(
    request: Request
):

    print("=== STRAVA REQUEST ===")
    print(
        "METHOD:",
        request.method
    )

    # -----------------------------------
    # STRAVA VERIFICATION
    # -----------------------------------

    if request.method == "GET":

        params = dict(
            request.query_params
        )

        print(
            "QUERY PARAMS:",
            params
        )

        if "hub.challenge" in params:

            print(
                "CHALLENGE RECEIVED"
            )

            return {
                "hub.challenge":
                params["hub.challenge"]
            }

        return {"status": "ok"}

    # -----------------------------------
    # STRAVA EVENTS
    # -----------------------------------

    data = await request.json()

    print(
        "STRAVA EVENT:",
        data
    )

    # -----------------------------------
    # ONLY NEW ACTIVITIES
    # -----------------------------------

    if (
        data.get("object_type")
        == "activity"
        and
        data.get("aspect_type")
        == "create"
    ):

        activity_id = data.get(
            "object_id"
        )

        print(
            "NEW ACTIVITY ID:",
            activity_id
        )

        # -----------------------------------
        # REFRESH ACCESS TOKEN
        # -----------------------------------

        fresh_access_token = (
            refresh_access_token()
        )

        headers = {
            "Authorization":
            f"Bearer "
            f"{fresh_access_token}"
        }

        response = requests.get(
            f"https://www.strava.com/"
            f"api/v3/activities/"
            f"{activity_id}",
            headers=headers
        )

        print(
            "STRAVA API STATUS:",
            response.status_code
        )

        activity = response.json()

        print(
            "ACTIVITY DATA:",
            activity
        )

        # -----------------------------------
        # RUN DATA
        # -----------------------------------

        distance_km = round(
            activity.get(
                "distance",
                0
            ) / 1000,
            2
        )

        print(
            "DISTANCE CHECK:",
            distance_km
        )

        # -----------------------------------
        # ONLY RUNS
        # -----------------------------------

        if (
            activity.get("type")
            == "Run"
        ):

            name = activity.get(
                "name"
            )

            moving_time = (
                activity.get(
                    "moving_time",
                    0
                )
            )

            if distance_km > 0:

                pace_seconds = (
                    moving_time /
                    distance_km
                )

                minutes = int(
                    pace_seconds // 60
                )

                seconds = int(
                    pace_seconds % 60
                )

                pace = (
                    f"{minutes}:"
                    f"{seconds:02d}/km"
                )

            else:

                pace = "N/A"

            average_hr = (
                activity.get(
                    "average_heartrate"
                )
            )

            print(
                "=== RUN DETECTED ==="
            )

            print(
                "NAME:",
                name
            )

            print(
                "DISTANCE:",
                distance_km
            )

            print(
                "PACE:",
                pace
            )

            print(
                "AVG HR:",
                average_hr
            )

            # -----------------------------------
            # SAVE TO DATABASE
            # -----------------------------------

            try:

                supabase.table(
                    "runs"
                ).insert({
                    "id":
                    activity_id,

                    "name":
                    name,

                    "distance_km":
                    distance_km,

                    "moving_time":
                    moving_time,

                    "pace":
                    pace,

                    "average_hr":
                    average_hr
                }).execute()

                print(
                    "RUN SAVED "
                    "TO DATABASE"
                )

            except Exception as e:

                print(
                    "DATABASE ERROR:",
                    e
                )

            # -----------------------------------
            # METRICS
            # -----------------------------------

            metrics = (
                calculate_metrics(
                    supabase
                )
            )

            print(
                "WEEKLY METRICS:",
                metrics
            )

            # -----------------------------------
            # PREDICTION
            # -----------------------------------

            prediction = (
                predict_marathon(
                    metrics
                )
            )

            print(
                "MARATHON "
                "PREDICTION:",
                prediction
            )

            # -----------------------------------
            # RECOVERY
            # -----------------------------------

            recovery = (
                calculate_recovery_status(
                    supabase
                )
            )

            print(
                "RECOVERY:",
                recovery
            )

            # -----------------------------------
            # TRAINING PLAN
            # -----------------------------------

            recommendation = (
                generate_training_recommendation(
                    metrics,
                    prediction
                )
            )

            print(
                "TRAINING "
                "RECOMMENDATION:",
                recommendation
            )

            # -----------------------------------
            # AI COACHING
            # -----------------------------------

            run_data = {
                "distance_km":
                distance_km,

                "pace":
                pace,

                "average_hr":
                average_hr
            }

            try:

                ai_feedback = (
                    generate_coaching_feedback(
                        run_data,
                        metrics
                    )
                )

                print(
                    "AI FEEDBACK:",
                    ai_feedback
                )

            except Exception as e:

                print(
                    "AI ERROR:",
                    e
                )

                ai_feedback = (
                    "AI coaching "
                    "midlertidigt "
                    "utilgængelig."
                )

            # -----------------------------------
            # TELEGRAM FEEDBACK
            # -----------------------------------

            feedback = (
                f"🏃 Ny løbetur "
                f"registreret\n\n"

                f"Navn: {name}\n"

                f"Distance: "
                f"{distance_km} km\n"

                f"Pace: {pace}\n"

                f"Puls: "
                f"{average_hr}\n\n"

                f"📊 Ugens statistik\n"

                f"Ugens km: "
                f"{metrics['weekly_distance']}\n"

                f"Antal løb: "
                f"{metrics['run_count']}\n"

                f"Gns pace: "
                f"{metrics['average_pace']}"
            )

            if (
                metrics[
                    "fatigue_warning"
                ]
            ):

                feedback += (
                    "\n\n⚠ Belastningen "
                    "er høj."
                )

            feedback += (
                f"\n\n🤖 AI Coach\n"
                f"{ai_feedback}"
            )

            feedback += (
                f"\n\n🏁 Marathon "
                f"Prediction\n"

                f"Tid: "
                f"{prediction['predicted_time']}\n"

                f"Readiness: "
                f"{prediction['readiness_score']}"
                f"/100\n"

                f"Sub 4 chance: "
                f"{prediction['sub4_probability']}"
                f"%"
            )

            feedback += (
                f"\n\n🩺 Recovery "
                f"Status\n"

                f"Acute load: "
                f"{recovery['acute_load']} km\n"

                f"Chronic load: "
                f"{recovery['chronic_load']} km\n"

                f"Ratio: "
                f"{recovery['load_ratio']}\n\n"

                f"{recovery['message']}"
            )

            feedback += (
                f"\n\n📅 Næste "
                f"anbefaling\n"

                f"{recommendation}"
            )

            # -----------------------------------
            # SEND TELEGRAM FEEDBACK
            # -----------------------------------

            try:

                requests.post(
                    f"https://api.telegram.org/"
                    f"bot{TELEGRAM_BOT_TOKEN}/"
                    f"sendMessage",
                    json={
                        "chat_id":
                        TELEGRAM_CHAT_ID,

                        "text":
                        feedback
                    }
                )

                print(
                    "TELEGRAM "
                    "MESSAGE SENT"
                )

            except Exception as e:

                print(
                    "TELEGRAM ERROR:",
                    e
                )

    return {"ok": True}
