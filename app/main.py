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

from app.services.garmin_service import (
    sync_garmin_health_to_supabase
)

from app.services.recovery_engine import (
    calculate_readiness_score
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
# SUPABASE
# -----------------------------------

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
# GARMIN TEST
# -----------------------------------

@app.get("/garmin-test")
def garmin_test():

    try:

        data = (
            sync_garmin_health_to_supabase(
                supabase
            )
        )

        readiness = (
            calculate_readiness_score(

                sleep_hours=data.get(
                    "sleep_hours"
                ),

                hrv=data.get(
                    "hrv"
                ),

                body_battery=data.get(
                    "body_battery"
                ),

                resting_hr=data.get(
                    "resting_hr"
                )
            )
        )

        return {

            "status": "success",

            "health": data,

            "recovery": readiness
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
    # METRICS
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

    readiness = (
        calculate_readiness_score(

            sleep_hours=health.get(
                "sleep_hours"
            ),

            hrv=health.get(
                "hrv"
            ),

            body_battery=health.get(
                "body_battery"
            ),

            resting_hr=health.get(
                "resting_hr"
            )
        )
    )

    response_text = None

    # -----------------------------------
    # STATUS
    # -----------------------------------

    if text == "/status":

        response_text = (
            "📊 Marathon Coach\n\n"

            f"Km this week: "
            f"{metrics['weekly_distance']}\n"

            f"Runs: "
            f"{metrics['run_count']}\n"

            f"Average pace: "
            f"{metrics['average_pace']}\n\n"

            f"🏁 Readiness: "
            f"{prediction['readiness_score']}/100\n"

            f"🧠 Fitness: "
            f"{fitness['score']}/100\n"

            f"🧬 Recovery V4: "
            f"{recovery_v4['score']}/100\n"

            f"⚡ Recovery Engine: "
            f"{readiness['score']}/100\n"

            f"📈 Status: "
            f"{readiness['status']}"
        )

    # -----------------------------------
    # HEALTH
    # -----------------------------------

    elif text == "/health":

        if not health:

            response_text = (
                "No health data yet."
            )

        else:

            response_text = (
                "🧬 Garmin Health\n\n"

                f"😴 Sleep: "
                f"{health.get('sleep_hours')} h\n"

                f"📉 HRV: "
                f"{health.get('hrv')}\n"

                f"🔋 Body Battery: "
                f"{health.get('body_battery')}\n"

                f"❤️ Resting HR: "
                f"{health.get('resting_hr')}\n\n"

                f"⚡ Readiness Score: "
                f"{readiness['score']}/100\n"

                f"📈 Status: "
                f"{readiness['status']}"
            )

    # -----------------------------------
    # DEFAULT
    # -----------------------------------

    else:

        response_text = (
            "Commands:\n\n"
            "/status\n"
            "/health"
