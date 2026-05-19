from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import os
from datetime import datetime

from app.services.garmin_service import (
    sync_garmin_health_to_supabase
)

from app.services.recovery_engine import (
    calculate_readiness_score
)

from app.services.fatigue_engine import (
    calculate_fatigue_score
)

from app.services.training_plan_service import (
    generate_weekly_plan
)

app = FastAPI()

# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():

    return {
        "status": "running",
        "service": "Marathon Coach AI",
        "version": "Recovery Intelligence V5"
    }

# ==================================================
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

# ==================================================
# GARMIN TEST
# ==================================================

@app.get("/garmin-test")
def garmin_test():

    try:

        garmin_data = sync_garmin_health_to_supabase()

        recovery = calculate_readiness_score(
            sleep_hours=garmin_data.get("sleep_hours"),
            hrv=garmin_data.get("hrv"),
            body_battery=garmin_data.get("body_battery"),
            resting_hr=garmin_data.get("resting_hr"),
            weight=garmin_data.get("weight"),
        )

        fatigue = calculate_fatigue_score(
            sleep_hours=garmin_data.get("sleep_hours"),
            hrv=garmin_data.get("hrv"),
            body_battery=garmin_data.get("body_battery"),
            resting_hr=garmin_data.get("resting_hr"),
            weight=garmin_data.get("weight"),
        )

        return {
            "status": "success",
            "data": garmin_data,
            "recovery": recovery,
            "fatigue": fatigue
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# ==================================================
# WEEK PLAN
# ==================================================

@app.get("/week")
def week():

    try:

        plan = generate_weekly_plan()

        return {
            "status": "success",
            "plan": plan
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# ==================================================
# PLAN
# ==================================================

@app.get("/plan")
def plan():

    try:

        plan = generate_weekly_plan()

        return {
            "status": "success",
            "plan": plan
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# ==================================================
# RECOVERY ENDPOINT
# ==================================================

@app.get("/recovery")
def recovery():

    try:

        garmin_data = sync_garmin_health_to_supabase()

        recovery_data = calculate_readiness_score(
            sleep_hours=garmin_data.get("sleep_hours"),
            hrv=garmin_data.get("hrv"),
            body_battery=garmin_data.get("body_battery"),
            resting_hr=garmin_data.get("resting_hr"),
            weight=garmin_data.get("weight"),
        )

        fatigue_data = calculate_fatigue_score(
            sleep_hours=garmin_data.get("sleep_hours"),
            hrv=garmin_data.get("hrv"),
            body_battery=garmin_data.get("body_battery"),
            resting_hr=garmin_data.get("resting_hr"),
            weight=garmin_data.get("weight"),
        )

        return {
            "status": "success",
            "recovery": recovery_data,
            "fatigue": fatigue_data
        }

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }

# ==================================================
# TELEGRAM WEBHOOK
# ==================================================

@app.post("/telegram")
async def telegram_webhook(request: Request):

    try:

        payload = await request.json()

        message = payload.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if not text:

            return JSONResponse(
                content={"status": "ignored"}
            )

        response_text = process_command(text)

        send_telegram_message(
            chat_id,
            response_text
        )

        return JSONResponse(
            content={"status": "ok"}
        )

    except Exception as e:

        return JSONResponse(
            content={
                "status": "error",
                "message": str(e)
            }
        )

# ==================================================
# COMMAND PROCESSOR
# ==================================================

def process_command(text):

    command = text.lower().strip()

    # --------------------------------------------------
    # /health
    # --------------------------------------------------

    if command == "/health":

        return (
            "✅ Marathon Coach AI online"
        )

    # --------------------------------------------------
    # /status
    # --------------------------------------------------

    elif command == "/status":

        return (
            "🧠 Marathon Coach AI\n"
            "Recovery Intelligence V5 ACTIVE\n"
            "Garmin sync ENABLED\n"
            "Fatigue engine ENABLED\n"
            "Telegram ENABLED"
        )

    # --------------------------------------------------
    # /week
    # --------------------------------------------------

    elif command == "/week":

        plan = generate_weekly_plan()

        return (
            "📅 Weekly Training Plan\n\n"
            f"{plan}"
        )

    # --------------------------------------------------
    # /plan
    # --------------------------------------------------

    elif command == "/plan":

        plan = generate_weekly_plan()

        return (
            "🏃 Current Training Plan\n\n"
            f"{plan}"
        )

    # --------------------------------------------------
    # /recovery
    # --------------------------------------------------

    elif command == "/recovery":

        garmin_data = sync_garmin_health_to_supabase()

        recovery = calculate_readiness_score(
            sleep_hours=garmin_data.get("sleep_hours"),
            hrv=garmin_data.get("hrv"),
            body_battery=garmin_data.get("body_battery"),
            resting_hr=garmin_data.get("resting_hr"),
            weight=garmin_data.get("weight"),
        )

        fatigue = calculate_fatigue_score(
            sleep_hours=garmin_data.get("sleep_hours"),
            hrv=garmin_data.get("hrv"),
            body_battery=garmin_data.get("body_battery"),
            resting_hr=garmin_data.get("resting_hr"),
            weight=garmin_data.get("weight"),
        )

        return (
            "🧠 Recovery Intelligence V5\n\n"
            f"Recovery Score: {recovery.get('score')}\n"
            f"Recovery Status: {recovery.get('status')}\n\n"
            f"Fatigue Score: {fatigue.get('fatigue_score')}\n"
            f"Fatigue Status: {fatigue.get('fatigue_status')}\n\n"
            f"Recommendation:\n"
            f"{fatigue.get('recommendation')}"
        )

    # --------------------------------------------------
    # /fatigue
    # --------------------------------------------------

    elif command == "/fatigue":

        garmin_data = sync_garmin_health_to_supabase()

        fatigue = calculate_fatigue_score(
            sleep_hours=garmin_data.get("sleep_hours"),
            hrv=garmin_data.get("hrv"),
            body_battery=garmin_data.get("body_battery"),
            resting_hr=garmin_data.get("resting_hr"),
            weight=garmin_data.get("weight"),
        )

        explanation_text = "\n".join(
            [f"• {x}" for x in fatigue.get("explanations", [])]
        )

        return (
            "⚡ Fatigue Analysis\n\n"
            f"Fatigue Score: {fatigue.get('fatigue_score')}\n"
            f"Status: {fatigue.get('fatigue_status')}\n\n"
            f"{explanation_text}\n\n"
            f"Recommendation:\n"
            f"{fatigue.get('recommendation')}"
        )

    # --------------------------------------------------
    # /metrics
    # --------------------------------------------------

    elif command == "/metrics":

        garmin_data = sync_garmin_health_to_supabase()

        return (
            "📊 Latest Garmin Metrics\n\n"
            f"Sleep: {garmin_data.get('sleep_hours')} h\n"
            f"HRV: {garmin_data.get('hrv')}\n"
            f"Body Battery: {garmin_data.get('body_battery')}\n"
            f"Resting HR: {garmin_data.get('resting_hr')}\n"
            f"Weight: {garmin_data.get('weight')}"
        )

    # --------------------------------------------------
    # UNKNOWN COMMAND
    # --------------------------------------------------

    return (
        "Unknown command\n\n"
        "Available commands:\n"
        "/health\n"
        "/status\n"
        "/week\n"
        "/plan\n"
        "/recovery\n"
        "/fatigue\n"
        "/metrics"
    )

# ==================================================
# TELEGRAM SEND MESSAGE
# ==================================================

def send_telegram_message(chat_id, text):

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:

        print("TELEGRAM_BOT_TOKEN missing")
        return

    url = (
        f"https://api.telegram.org/bot{token}/sendMessage"
    )

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=10
        )

        print(response.text)

    except Exception as e:

        print(
            f"Telegram send error: {e}"
        )
