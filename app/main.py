from fastapi import FastAPI, Request
import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler
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

from app.services.trend_service import (
    calculate_trend_analysis
)

from app.services.fitness_service import (
    calculate_fitness_score
)

from app.services.weekly_plan_service import (
    generate_weekly_plan
)

from app.services.adaptive_planner_service import (
    generate_daily_adaptive_plan
)

from app.services.health_service import (
    save_health_metric,
    get_latest_health_metrics
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
# ROOT
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
    # LOAD CORE DATA
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

    trend = (
        calculate_trend_analysis(
            supabase
        )
    )

    fitness = (
        calculate_fitness_score(
            metrics,
            recovery,
            trend
        )
    )

    # -----------------------------------
    # STATUS
    # -----------------------------------

    if text == "/status":

        response_text = (
            "📊 Status\n\n"

            f"Ugens km: "
            f"{metrics['weekly_distance']}\n"

            f"Antal løb: "
            f"{metrics['run_count']}\n"

            f"Gns pace: "
            f"{metrics['average_pace']}\n\n"

            f"🏁 Readiness: "
            f"{prediction['readiness_score']}/100\n"

            f"📈 Trend: "
            f"{trend['trend']}\n"

            f"🧠 Fitness: "
            f"{fitness['score']}/100\n\n"

            f"{fitness['message']}"
        )

    # -----------------------------------
    # TODAY
    # -----------------------------------

    elif text == "/today":

        recommendation = (
            generate_training_recommendation(
                metrics,
                prediction
            )
        )

        response_text = (
            "📅 Dagens anbefaling\n\n"

            f"{recommendation}\n\n"

            f"🩺 {recovery['message']}\n"

            f"📈 {trend['message']}\n\n"

            f"🧠 Fitness "
            f"{fitness['score']}/100"
        )

    # -----------------------------------
    # WEEKLY
    # -----------------------------------

    elif text == "/weekly":

        recommendation = (
            generate_training_recommendation(
                metrics,
                prediction
            )
        )

        response_text = (
            "📈 Weekly Summary\n\n"

            f"Distance: "
            f"{metrics['weekly_distance']} km\n"

            f"Løb: "
            f"{metrics['run_count']}\n"

            f"Pace: "
            f"{metrics['average_pace']}\n\n"

            f"🩺 {recovery['message']}\n"

            f"📈 {trend['message']}\n\n"

            f"🧠 Fitness "
            f"{fitness['score']}/100\n\n"

            f"{recommendation}"
        )

    # -----------------------------------
    # PREDICTION
    # -----------------------------------

    elif text == "/prediction":

        response_text = (
            "🏁 Marathon Prediction\n\n"

            f"Tid: "
            f"{prediction['predicted_time']}\n"

            f"Readiness: "
            f"{prediction['readiness_score']}/100\n"

            f"Sub4 chance: "
            f"{prediction['sub4_probability']}%\n\n"

            f"🧠 Fitness "
            f"{fitness['score']}/100"
        )

    # -----------------------------------
    # RECOVERY
    # -----------------------------------

    elif text == "/recovery":

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

    # -----------------------------------
    # TREND
    # -----------------------------------

    elif text == "/trend":

        response_text = (
            "📈 Trend Analysis\n\n"

            f"{trend['message']}\n\n"

            f"Seneste 14 dage: "
            f"{trend['recent_distance']} km\n"

            f"Forrige 14 dage: "
            f"{trend['older_distance']} km"
        )

    # -----------------------------------
    # FITNESS
    # -----------------------------------

    elif text == "/fitness":

        response_text = (
            "🧠 Fitness Score\n\n"

            f"{fitness['score']}/100\n"

            f"{fitness['label']}\n\n"

            f"{fitness['message']}"
        )

    # -----------------------------------
    # WEEKLY PLAN
    # -----------------------------------

    elif text == "/plan":

        plan = generate_weekly_plan(
            metrics,
            recovery,
            fitness,
            trend
        )

        response_text = (
            "🗓 Ugeplan\n\n"

            + "\n".join(
                plan["plan"]
            )

            + f"\n\nIntensitet: "
            f"{plan['intensity']}"
        )

    # -----------------------------------
    # ADAPTIVE PLAN
    # -----------------------------------

    elif text == "/adaptive":

        adaptive = (
            generate_daily_adaptive_plan(
                metrics,
                recovery,
                trend,
                fitness,
                prediction
            )
        )

        response_text = (
            "🧠 Adaptive Coach\n\n"

            f"Dag: "
            f"{adaptive['day']}\n"

            f"Intensitet: "
            f"{adaptive['intensity']}\n\n"

            f"{adaptive['workout']}"
        )

    # -----------------------------------
    # HEALTH STATUS
    # -----------------------------------

    elif text == "/health":

        health = (
            get_latest_health_metrics(
                supabase
            )
        )

        if not health:

            response_text = (
                "Ingen health data endnu."
            )

        else:

            response_text = (
                "🧬 Health Metrics\n\n"

                f"😴 Søvn: "
                f"{health.get('sleep_hours')}\n"

                f"❤️ HRV: "
                f"{health.get('hrv')}\n"

                f"🔋 Body Battery: "
                f"{health.get('body_battery')}\n"

                f"❤️ RHR: "
                f"{health.get('resting_hr')}\n"

                f"⚖ Vægt: "
                f"{health.get('weight')}"
            )

    # -----------------------------------
    # SAVE SLEEP
    # -----------------------------------

    elif text.startswith("/sleep"):

        try:

            value = float(
                text.split(" ")[1]
            )

            save_health_metric(
                supabase,
                "sleep_hours",
                value
            )

            response_text = (
                f"😴 Søvn gemt: "
                f"{value} timer"
            )

        except:

            response_text = (
                "Brug:\n"
                "/sleep 7.5"
            )

    # -----------------------------------
    # SAVE HRV
    # -----------------------------------

    elif text.startswith("/hrv"):

        try:

            value = int(
                text.split(" ")[1]
            )

            save_health_metric(
                supabase,
                "hrv",
                value
            )

            response_text = (
                f"❤️ HRV gemt: "
                f"{value}"
            )

        except:

            response_text = (
                "Brug:\n"
                "/hrv 62"
            )

    # -----------------------------------
    # SAVE BODY BATTERY
    # -----------------------------------

    elif text.startswith("/body"):

        try:

            value = int(
                text.split(" ")[1]
            )

            save_health_metric(
                supabase,
                "body_battery",
                value
            )

            response_text = (
                f"🔋 Body Battery gemt: "
                f"{value}"
            )

        except:

            response_text = (
                "Brug:\n"
                "/body 78"
            )

    # -----------------------------------
    # SAVE RESTING HR
    # -----------------------------------

    elif text.startswith("/rhr"):

        try:

            value = int(
                text.split(" ")[1]
            )

            save_health_metric(
                supabase,
                "resting_hr",
                value
            )

            response_text = (
                f"❤️ Resting HR gemt: "
                f"{value}"
            )

        except:

            response_text = (
                "Brug:\n"
                "/rhr 49"
            )

    # -----------------------------------
    # SAVE WEIGHT
    # -----------------------------------

    elif text.startswith("/weight"):

        try:

            value = float(
                text.split(" ")[1]
            )

            save_health_metric(
                supabase,
                "weight",
                value
            )

            response_text = (
                f"⚖ Vægt gemt: "
                f"{value} kg"
            )

        except:

            response_text = (
                "Brug:\n"
                "/weight 81.4"
            )

    # -----------------------------------
    # START
    # -----------------------------------

    elif text == "/start":

        response_text = (
            "🏃 AI Running Coach\n\n"

            "Kommandoer:\n\n"

            "/status\n"
            "/today\n"
            "/weekly\n"
            "/prediction\n"
            "/recovery\n"
            "/trend\n"
            "/fitness\n"
            "/plan\n"
            "/adaptive\n"
            "/health\n\n"

            "Health tracking:\n"

            "/sleep 7.5\n"
            "/hrv 62\n"
            "/body 78\n"
            "/rhr 49\n"
            "/weight 81.4"
        )

    # -----------------------------------
    # UNKNOWN
    # -----------------------------------

    else:

        response_text = (
            "Ukendt kommando.\n\n"

            "Prøv:\n\n"

            "/status\n"
            "/today\n"
            "/weekly\n"
            "/prediction\n"
            "/recovery\n"
            "/trend\n"
            "/fitness\n"
            "/plan\n"
            "/adaptive\n"
            "/health"
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
            "TELEGRAM MESSAGE SENT"
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

    # -----------------------------------
    # STRAVA VERIFY
    # -----------------------------------

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

    # -----------------------------------
    # STRAVA EVENT
    # -----------------------------------

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

        print(
            "NEW ACTIVITY:",
            activity_id
        )

        # -----------------------------------
        # REFRESH TOKEN
        # -----------------------------------

        access_token = (
            refresh_access_token()
        )

        headers = {
            "Authorization":
            f"Bearer {access_token}"
        }

        response = requests.get(
            f"https://www.strava.com/"
            f"api/v3/activities/"
            f"{activity_id}",
            headers=headers
        )

        print(
            "STRAVA STATUS:",
            response.status_code
        )

        activity = response.json()

        print(
            "ACTIVITY:",
            activity
        )

        # -----------------------------------
        # RUN ONLY
        # -----------------------------------

        if (
            activity.get("type")
            == "Run"
        ):

            name = activity.get(
                "name"
            )

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

            average_hr = activity.get(
                "average_heartrate"
            )

            # -----------------------------------
            # PACE
            # -----------------------------------

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

            # -----------------------------------
            # SAVE DATABASE
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
            # ANALYTICS
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

            trend = (
                calculate_trend_analysis(
                    supabase
                )
            )

            fitness = (
                calculate_fitness_score(
                    metrics,
                    recovery,
                    trend
                )
            )

            adaptive = (
                generate_daily_adaptive_plan(
                    metrics,
                    recovery,
                    trend,
                    fitness,
                    prediction
                )
            )

            weekly_plan = (
                generate_weekly_plan(
                    metrics,
                    recovery,
                    fitness,
                    trend
                )
            )

            # -----------------------------------
            # AI FEEDBACK
            # -----------------------------------

            try:

                ai_feedback = (
                    generate_coaching_feedback(
                        {
                            "distance_km":
                            distance_km,

                            "pace":
                            pace,

                            "average_hr":
                            average_hr
                        },
                        metrics
                    )
                )

            except Exception as e:

                print(
                    "AI ERROR:",
                    e
                )

                ai_feedback = (
                    "AI feedback "
                    "utilgængelig senere."
                )

            # -----------------------------------
            # TELEGRAM FEEDBACK
            # -----------------------------------

            feedback = (
                f"🏃 Ny løbetur\n\n"

                f"{name}\n"

                f"{distance_km} km\n"

                f"{pace}\n\n"

                f"🧠 Fitness: "
                f"{fitness['score']}/100\n"

                f"{fitness['message']}\n\n"

                f"🩺 {recovery['message']}\n\n"

                f"📈 {trend['message']}\n\n"

                f"🏁 Prediction: "
                f"{prediction['predicted_time']}\n\n"

                f"🤖 AI Coach\n"
                f"{ai_feedback}\n\n"

                f"🧠 Adaptive plan\n"
                f"{adaptive['workout']}\n\n"

                f"🗓 Plan preview\n"

                + "\n".join(
                    weekly_plan["plan"][:3]
                )
            )

            # -----------------------------------
            # SEND TELEGRAM
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
                    "TELEGRAM SENT"
                )

            except Exception as e:

                print(
                    "TELEGRAM ERROR:",
                    e
                )

    return {"ok": True}
