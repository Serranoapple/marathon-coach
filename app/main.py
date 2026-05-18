from fastapi import FastAPI, Request
import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from supabase import create_client

from app.services.metrics_service import calculate_metrics
from app.services.prediction_service import predict_marathon
from app.services.recovery_service import calculate_recovery_status
from app.services.trend_service import calculate_trend_analysis
from app.services.fitness_service import calculate_fitness_score

from app.services.training_plan_service import (
    generate_training_recommendation
)

from app.services.adaptive_planner_service import (
    generate_daily_adaptive_plan
)

from app.services.weekly_plan_service import (
    generate_weekly_plan
)

from app.services.health_service import (
    get_latest_health_metrics
)

from app.services.recovery_intelligence_v4 import (
    calculate_recovery_intelligence_v4
)

from app.services.briefing_service import (
    send_daily_briefing
)

from app.services.strava_service import (
    refresh_access_token
)

# -----------------------------------
# GARMIN IMPORT
# -----------------------------------

from app.services.garmin_service import (
    sync_garmin_health_to_supabase
)

print("MAIN.PY LOADED")

app = FastAPI()

# -----------------------------------
# ENV
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

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# -----------------------------------
# SCHEDULER
# -----------------------------------

scheduler = BackgroundScheduler()

# Daily briefing
scheduler.add_job(
    lambda: send_daily_briefing(
        supabase
    ),
    "cron",
    hour=5,
    minute=0
)

# Garmin sync
scheduler.add_job(
    lambda: sync_garmin_health_to_supabase(
        supabase
    ),
    "cron",
    hour=6,
    minute=0
)

scheduler.start()

print("SCHEDULER STARTED")

# -----------------------------------
# ROOT
# -----------------------------------

@app.get("/")
def root():

    return {
        "status": "running"
    }

# -----------------------------------
# GARMIN TEST ENDPOINT
# -----------------------------------

@app.get("/garmin-test")
def garmin_test():

    try:

        data = (
            sync_garmin_health_to_supabase(
                supabase
            )
        )

        return {
            "status": "success",
            "data": data
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
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

        return {
            "ok": True
        }

    # -----------------------------------
    # CORE PIPELINE
    # -----------------------------------

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

    trend = calculate_trend_analysis(
        supabase
    )

    fitness = calculate_fitness_score(
        metrics,
        recovery,
        trend
    )

    health = (
        get_latest_health_metrics(
            supabase
        ) or {}
    )

    recovery_v4 = (
        calculate_recovery_intelligence_v4(
            health,
            recovery,
            fitness,
            trend
        )
    )

    response_text = None

    # -----------------------------------
    # STATUS
    # -----------------------------------

    if text == "/status":

        response_text = (
            "📊 Status\n\n"
            f"Km: "
            f"{metrics['weekly_distance']}\n"

            f"Løb: "
            f"{metrics['run_count']}\n"

            f"Pace: "
            f"{metrics['average_pace']}\n\n"

            f"🏁 Readiness: "
            f"{prediction['readiness_score']}/100\n"

            f"🧠 Fitness: "
            f"{fitness['score']}/100\n"

            f"🧬 Recovery V4: "
            f"{recovery_v4['score']}/100\n"

            f"{recovery_v4['message']}"
        )

    # -----------------------------------
    # HEALTH
    # -----------------------------------

    elif text == "/health":

        if not health:

            response_text = (
                "Ingen health data endnu."
            )

        else:

            response_text = (
                "🧬 Garmin Health\n\n"

                f"Søvn: "
                f"{health.get('sleep_hours')}\n"

                f"HRV: "
                f"{health.get('hrv')}\n"

                f"Body Battery: "
                f"{health.get('body_battery')}\n"

                f"RHR: "
                f"{health.get('resting_hr')}"
            )

    # -----------------------------------
    # DEFAULT
    # -----------------------------------

    else:

        response_text = (
            "Kommandoer:\n\n"
            "/status\n"
            "/health"
        )

    # -----------------------------------
    # SEND TELEGRAM
    # -----------------------------------

    try:

        requests.post(
            f"https://api.telegram.org/bot"
            f"{TELEGRAM_BOT_TOKEN}"
            f"/sendMessage",

            json={
                "chat_id": chat_id,
                "text": response_text
            }
        )

        print(
            "TELEGRAM SENT"
        )

    except Exception as e:

        print(
            "TELEGRAM ERROR:",
            e
        )

    return {
        "ok": True
    }

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

    if request.method == "GET":

        params = dict(
            request.query_params
        )

        if "hub.challenge" in params:

            return {
                "hub.challenge":
                params["hub.challenge"]
            }

        return {
            "status": "ok"
        }

    data = await request.json()

    print(
        "STRAVA EVENT:",
        data
    )

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

        access_token = (
            refresh_access_token()
        )

        headers = {
            "Authorization":
            f"Bearer {access_token}"
        }

        activity = requests.get(
            f"https://www.strava.com/api/v3/activities/{activity_id}",
            headers=headers
        ).json()

        if activity.get("type") != "Run":

            return {
                "ok": True
            }

        distance_km = round(
            activity.get(
                "distance",
                0
            ) / 1000,
            2
        )

        moving_time = activity.get(
            "moving_time",
            0
        )

        avg_hr = activity.get(
            "average_heartrate"
        )

        pace = "N/A"

        if distance_km > 0:

            pace_sec = (
                moving_time /
                distance_km
            )

            pace = (
                f"{int(pace_sec//60)}:"
                f"{int(pace_sec%60):02d}/km"
            )

        supabase.table(
            "runs"
        ).insert({

            "id":
            activity_id,

            "name":
            activity.get("name"),

            "distance_km":
            distance_km,

            "moving_time":
            moving_time,

            "pace":
            pace,

            "average_hr":
            avg_hr

        }).execute()

        print(
            "RUN SAVED"
        )

    return {
        "ok": True
    }
