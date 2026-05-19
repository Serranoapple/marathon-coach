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

# --------------------------------------------------
# ENV
# --------------------------------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# --------------------------------------------------
# SCHEDULER
# --------------------------------------------------

scheduler = BackgroundScheduler()

scheduler.add_job(
    lambda: send_daily_briefing(supabase),
    "cron",
    hour=5,
    minute=0
)

scheduler.add_job(
    lambda: sync_garmin_health_to_supabase(supabase),
    "cron",
    hour=6,
    minute=0
)

scheduler.start()

print("SCHEDULER STARTED")

# --------------------------------------------------
# ROOT
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "status": "running"
    }

# --------------------------------------------------
# GARMIN TEST
# --------------------------------------------------

@app.get("/garmin-test")
def garmin_test():

    try:

        data = sync_garmin_health_to_supabase(
            supabase
        )

        readiness = calculate_readiness_score(
            sleep_hours=data.get("sleep_hours"),
            hrv=data.get("hrv"),
            body_battery=data.get("body_battery"),
            resting_hr=data.get("resting_hr"),
            weight=data.get("weight")
        )

        return {
            "status": "success",
            "data": data,
            "recovery": readiness
        }

    except Exception as e:

        print("GARMIN TEST ERROR:", e)

        return {
            "status": "error",
            "message": str(e)
        }

# --------------------------------------------------
# TELEGRAM WEBHOOK
# --------------------------------------------------

@app.post("/telegram")
async def telegram_webhook(request: Request):

    try:

        data = await request.json()

        print("TELEGRAM WEBHOOK HIT")
        print(data)

        message = data.get("message", {})

        text = (
            message.get("text", "") or ""
        ).strip().lower()

        chat_id = message.get(
            "chat",
            {}
        ).get("id")

        print("TEXT:", text)
        print("CHAT ID:", chat_id)

        if not chat_id:

            return {"ok": True}

        # --------------------------------------------------
        # LOAD SERVICES SAFE
        # --------------------------------------------------

        try:

            metrics = calculate_metrics(
                supabase
            )

        except Exception as e:

            print("METRICS ERROR:", e)

            metrics = {
                "weekly_distance": 0,
                "run_count": 0,
                "average_pace": "N/A"
            }

        try:

            prediction = predict_marathon(
                metrics
            )

        except Exception as e:

            print("PREDICTION ERROR:", e)

            prediction = {
                "readiness_score": 0
            }

        try:

            recovery = calculate_recovery_status(
                supabase
            )

        except Exception as e:

            print("RECOVERY ERROR:", e)

            recovery = {}

        try:

            trend = calculate_trend_analysis(
                supabase
            )

        except Exception as e:

            print("TREND ERROR:", e)

            trend = {}

        try:

            fitness = calculate_fitness_score(
                metrics,
                recovery,
                trend
            )

        except Exception as e:

            print("FITNESS ERROR:", e)

            fitness = {
                "score": 0
            }

        try:

            health = get_latest_health_metrics(
                supabase
            ) or {}

        except Exception as e:

            print("HEALTH ERROR:", e)

            health = {}

        try:

            recovery_v4 = (
                calculate_recovery_intelligence_v4(
                    health,
                    recovery,
                    fitness,
                    trend
                )
            )

        except Exception as e:

            print("RECOVERY V4 ERROR:", e)

            recovery_v4 = {
                "score": 0
            }

        try:

            readiness = calculate_readiness_score(
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
                ),
                weight=health.get(
                    "weight"
                )
            )

        except Exception as e:

            print("READINESS ERROR:", e)

            readiness = {
                "score": 0,
                "status": "ERROR"
            }

        # --------------------------------------------------
        # COMMANDS
        # --------------------------------------------------

        response_text = None

        if text == "/status":

            response_text = (
                "📊 Marathon Coach\n\n"

                f"Km this week: "
                f"{metrics.get('weekly_distance', 0)}\n"

                f"Runs: "
                f"{metrics.get('run_count', 0)}\n"

                f"Average pace: "
                f"{metrics.get('average_pace', 'N/A')}\n\n"

                f"🏁 Readiness: "
                f"{prediction.get('readiness_score', 0)}/100\n"

                f"🧠 Fitness: "
                f"{fitness.get('score', 0)}/100\n"

                f"🧬 Recovery V4: "
                f"{recovery_v4.get('score', 0)}/100\n"

                f"⚡ Recovery Engine: "
                f"{readiness.get('score', 0)}/100\n\n"

                f"📈 Status: "
                f"{readiness.get('status', 'UNKNOWN')}"
            )

        elif text == "/health":

            response_text = (
                "🧬 Garmin Health\n\n"

                f"😴 Sleep: "
                f"{health.get('sleep_hours')}\n"

                f"📉 HRV: "
                f"{health.get('hrv')}\n"

                f"🔋 Body Battery: "
                f"{health.get('body_battery')}\n"

                f"❤️ Resting HR: "
                f"{health.get('resting_hr')}\n"

                f"⚖️ Weight: "
                f"{health.get('weight')}\n\n"

                f"⚡ Readiness: "
                f"{readiness.get('score')}/100\n"

                f"📈 Status: "
                f"{readiness.get('status')}"
            )

        elif text == "/plan":

            try:

                plan = (
                    generate_training_recommendation(
                        metrics,
                        readiness,
                        recovery_v4
                    )
                )

                response_text = (
                    f"🏃 Training Plan\n\n{plan}"
                )

            except Exception as e:

                print("PLAN ERROR:", e)

                response_text = (
                    "Training plan unavailable."
                )

        elif text == "/today":

            try:

                plan = (
                    generate_daily_adaptive_plan(
                        metrics,
                        readiness,
                        recovery_v4
                    )
                )

                response_text = (
                    f"🎯 Today's Plan\n\n{plan}"
                )

            except Exception as e:

                print("TODAY ERROR:", e)

                response_text = (
                    "Today's plan unavailable."
                )

        elif text == "/week":

            try:

                plan = generate_weekly_plan(
                    metrics,
                    readiness,
                    recovery_v4
                )

                response_text = (
                    f"📅 Weekly Plan\n\n{plan}"
                )

            except Exception as e:

                print("WEEK ERROR:", e)

                response_text = (
                    "Weekly plan unavailable."
                )

        elif text == "/recovery":

            response_text = (
                "🧬 Recovery Engine\n\n"

                f"Score: "
                f"{readiness.get('score')}/100\n"

                f"Status: "
                f"{readiness.get('status')}\n\n"

                f"HRV: "
                f"{health.get('hrv')}\n"

                f"Sleep: "
                f"{health.get('sleep_hours')}h\n"

                f"Body Battery: "
                f"{health.get('body_battery')}\n"

                f"Resting HR: "
                f"{health.get('resting_hr')}\n"

                f"Weight: "
                f"{health.get('weight')}"
            )

        else:

            response_text = (
                "📌 Commands:\n\n"

                "/status\n"
                "/health\n"
                "/plan\n"
                "/today\n"
                "/week\n"
                "/recovery"
            )

        # --------------------------------------------------
        # SEND TELEGRAM MESSAGE
        # --------------------------------------------------

        telegram_response = requests.post(
            f"https://api.telegram.org/bot"
            f"{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": response_text
            }
        )

        print(
            "TELEGRAM SEND RESPONSE:",
            telegram_response.text
        )

        return {"ok": True}

    except Exception as e:

        print("TELEGRAM FATAL ERROR:", e)

        return {
            "ok": False,
            "error": str(e)
        }

# --------------------------------------------------
# STRAVA WEBHOOK
# --------------------------------------------------

@app.api_route(
    "/strava-webhook",
    methods=["GET", "POST"]
)
async def strava_webhook(request: Request):

    if request.method == "GET":

        params = dict(
            request.query_params
        )

        if "hub.challenge" in params:

            return {
                "hub.challenge":
                params["hub.challenge"]
            }

        return {"status": "ok"}

    data = await request.json()

    print("STRAVA WEBHOOK:", data)

    if (
        data.get("object_type") == "activity"
        and data.get("aspect_type") == "create"
    ):

        activity_id = data.get("object_id")

        access_token = refresh_access_token()

        headers = {
            "Authorization":
            f"Bearer {access_token}"
        }

        activity = requests.get(
            f"https://www.strava.com/api/v3/"
            f"activities/{activity_id}",
            headers=headers
        ).json()

        print("ACTIVITY:", activity)

        if activity.get("type") != "Run":

            return {"ok": True}

        distance_km = round(
            activity.get("distance", 0) / 1000,
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
                moving_time / distance_km
            )

            pace = (
                f"{int(pace_sec // 60)}:"
                f"{int(pace_sec % 60):02d}/km"
            )

        try:

            supabase.table("runs").insert({

                "id": activity_id,
                "name": activity.get("name"),
                "distance_km": distance_km,
                "moving_time": moving_time,
                "pace": pace,
                "average_hr": avg_hr

            }).execute()

            print("RUN INSERTED")

        except Exception as e:

            print("SUPABASE INSERT ERROR:", e)

    return {"ok": True}
