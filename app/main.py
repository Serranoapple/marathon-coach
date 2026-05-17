from fastapi import FastAPI, Request
import os
import requests

from apscheduler.schedulers.background import BackgroundScheduler
from supabase import create_client

from app.services.metrics_service import calculate_metrics
from app.services.ai_service import generate_coaching_feedback
from app.services.prediction_service import predict_marathon
from app.services.strava_service import refresh_access_token
from app.services.training_plan_service import generate_training_recommendation
from app.services.briefing_service import send_daily_briefing

from app.services.recovery_service import calculate_recovery_status
from app.services.trend_service import calculate_trend_analysis
from app.services.fitness_service import calculate_fitness_score

print("MAIN.PY LOADED")

app = FastAPI()

# -----------------------------------
# ENV
# -----------------------------------

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# -----------------------------------
# SCHEDULER
# -----------------------------------

scheduler = BackgroundScheduler()

scheduler.add_job(
    lambda: send_daily_briefing(supabase),
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
    return {"status": "running"}

# -----------------------------------
# TELEGRAM WEBHOOK
# -----------------------------------

@app.post("/telegram")
async def telegram_webhook(request: Request):

    data = await request.json()

    message = data.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not chat_id:
        return {"ok": True}

    response_text = None

    # -----------------------------------
    # STATUS
    # -----------------------------------

    if text == "/status":

        metrics = calculate_metrics(supabase)
        prediction = predict_marathon(metrics)
        recovery = calculate_recovery_status(supabase)
        trend = calculate_trend_analysis(supabase)
        fitness = calculate_fitness_score(metrics, recovery, trend)

        response_text = (
            "📊 System status\n\n"
            f"Km: {metrics['weekly_distance']}\n"
            f"Løb: {metrics['run_count']}\n"
            f"Pace: {metrics['average_pace']}\n"
            f"Readiness: {prediction['readiness_score']}/100\n"
            f"Recovery: {recovery['status']}\n"
            f"Trend: {trend['trend']}\n\n"
            f"🧠 Fitness: {fitness['score']}/100\n"
            f"{fitness['message']}"
        )

    # -----------------------------------
    # TODAY
    # -----------------------------------

    elif text == "/today":

        metrics = calculate_metrics(supabase)
        prediction = predict_marathon(metrics)
        recovery = calculate_recovery_status(supabase)
        trend = calculate_trend_analysis(supabase)
        fitness = calculate_fitness_score(metrics, recovery, trend)

        recommendation = generate_training_recommendation(metrics, prediction)

        response_text = (
            "📅 Dagens plan\n\n"
            f"{recommendation}\n\n"
            f"🩺 {recovery['message']}\n"
            f"📈 {trend['message']}\n"
            f"🧠 Fitness: {fitness['score']}/100\n"
            f"{fitness['message']}"
        )

    # -----------------------------------
    # WEEKLY
    # -----------------------------------

    elif text == "/weekly":

        metrics = calculate_metrics(supabase)
        prediction = predict_marathon(metrics)
        recovery = calculate_recovery_status(supabase)
        trend = calculate_trend_analysis(supabase)
        fitness = calculate_fitness_score(metrics, recovery, trend)

        recommendation = generate_training_recommendation(metrics, prediction)

        response_text = (
            "📈 Weekly Summary\n\n"
            f"{metrics['weekly_distance']} km\n"
            f"{metrics['run_count']} løb\n"
            f"{metrics['average_pace']}\n\n"
            f"🩺 {recovery['message']}\n"
            f"📈 {trend['message']}\n"
            f"🧠 Fitness: {fitness['score']}/100\n"
            f"{fitness['message']}\n\n"
            f"📅 {recommendation}"
        )

    # -----------------------------------
    # PREDICTION
    # -----------------------------------

    elif text == "/prediction":

        metrics = calculate_metrics(supabase)
        prediction = predict_marathon(metrics)
        recovery = calculate_recovery_status(supabase)
        trend = calculate_trend_analysis(supabase)
        fitness = calculate_fitness_score(metrics, recovery, trend)

        response_text = (
            "🏁 Marathon Prediction\n\n"
            f"Tid: {prediction['predicted_time']}\n"
            f"Readiness: {prediction['readiness_score']}/100\n"
            f"Sub4: {prediction['sub4_probability']}%\n\n"
            f"🩺 {recovery['message']}\n"
            f"📈 {trend['message']}\n"
            f"🧠 Fitness: {fitness['score']}/100\n"
            f"{fitness['message']}"
        )

    # -----------------------------------
    # RECOVERY
    # -----------------------------------

    elif text == "/recovery":

        recovery = calculate_recovery_status(supabase)

        response_text = (
            "🩺 Recovery\n\n"
            f"{recovery['message']}\n\n"
            f"Ratio: {recovery['load_ratio']}"
        )

    # -----------------------------------
    # TREND
    # -----------------------------------

    elif text == "/trend":

        trend = calculate_trend_analysis(supabase)

        response_text = (
            "📈 Trend\n\n"
            f"{trend['message']}\n\n"
            f"{trend['recent_distance']} km vs {trend['older_distance']} km"
        )

    # -----------------------------------
    # FITNESS
    # -----------------------------------

    elif text == "/fitness":

        metrics = calculate_metrics(supabase)
        recovery = calculate_recovery_status(supabase)
        trend = calculate_trend_analysis(supabase)
        fitness = calculate_fitness_score(metrics, recovery, trend)

        response_text = (
            "🧠 Fitness Score\n\n"
            f"{fitness['score']}/100\n"
            f"{fitness['label']}\n"
            f"{fitness['message']}"
        )

    # -----------------------------------
    # DEFAULT
    # -----------------------------------

    else:

        response_text = (
            "Kommandoer:\n"
            "/status\n"
            "/today\n"
            "/weekly\n"
            "/prediction\n"
            "/recovery\n"
            "/trend\n"
            "/fitness"
        )

    # -----------------------------------
    # SEND TELEGRAM
    # -----------------------------------

    try:

        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": response_text
            }
        )

        print("TELEGRAM SENT")

    except Exception as e:
        print("TELEGRAM ERROR:", e)

    return {"ok": True}

# -----------------------------------
# STRAVA WEBHOOK
# -----------------------------------

@app.api_route("/strava-webhook", methods=["GET", "POST"])
async def strava_webhook(request: Request):

    if request.method == "GET":

        params = dict(request.query_params)

        if "hub.challenge" in params:
            return {"hub.challenge": params["hub.challenge"]}

        return {"status": "ok"}

    data = await request.json()

    if (
        data.get("object_type") == "activity"
        and data.get("aspect_type") == "create"
    ):

        activity_id = data.get("object_id")

        token = refresh_access_token()

        headers = {"Authorization": f"Bearer {token}"}

        response = requests.get(
            f"https://www.strava.com/api/v3/activities/{activity_id}",
            headers=headers
        )

        activity = response.json()

        distance_km = round(activity.get("distance", 0) / 1000, 2)

        if activity.get("type") == "Run":

            supabase.table("runs").insert({
                "id": activity_id,
                "name": activity.get("name"),
                "distance_km": distance_km,
                "moving_time": activity.get("moving_time", 0),
                "pace": None,
                "average_hr": activity.get("average_heartrate")
            }).execute()

            metrics = calculate_metrics(supabase)
            prediction = predict_marathon(metrics)
            recovery = calculate_recovery_status(supabase)
            trend = calculate_trend_analysis(supabase)
            fitness = calculate_fitness_score(metrics, recovery, trend)

            feedback = (
                f"🏃 Run registered\n\n"
                f"{activity.get('name')}\n"
                f"{distance_km} km\n\n"
                f"🧠 Fitness: {fitness['score']}/100\n"
                f"{fitness['message']}"
            )

            requests.post(
                f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": TELEGRAM_CHAT_ID,
                    "text": feedback
                }
            )

    return {"ok": True}
