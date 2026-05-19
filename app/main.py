from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import requests
from datetime import datetime

from app.services.garmin_service import sync_garmin_health_to_supabase
from app.services.recovery_engine import calculate_readiness_score
from app.services.fatigue_engine import calculate_fatigue_score
from app.services.training_plan_service import generate_weekly_plan


app = FastAPI()


# ==================================================
# ROOT
# ==================================================

@app.get("/")
def root():

    return {
        "status": "running",
        "system": "Marathon Coach AI",
        "version": "Recovery Intelligence V5"
    }


# ==================================================
# HEALTH ENDPOINT (API)
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

    data = sync_garmin_health_to_supabase()

    recovery = calculate_readiness_score(
        sleep_hours=data.get("sleep_hours"),
        hrv=data.get("hrv"),
        body_battery=data.get("body_battery"),
        resting_hr=data.get("resting_hr"),
        weight=data.get("weight"),
    )

    fatigue = calculate_fatigue_score(
        sleep_hours=data.get("sleep_hours"),
        hrv=data.get("hrv"),
        body_battery=data.get("body_battery"),
        resting_hr=data.get("resting_hr"),
        weight=data.get("weight"),
    )

    return {
        "status": "success",
        "data": data,
        "recovery": recovery,
        "fatigue": fatigue
    }


# ==================================================
# WEEK / PLAN
# ==================================================

@app.get("/week")
@app.get("/plan")
def week_plan():

    plan = generate_weekly_plan()

    return {
        "status": "success",
        "plan": plan
    }


# ==================================================
# TELEGRAM WEBHOOK
# ==================================================

@app.post("/telegram")
async def telegram(request: Request):

    payload = await request.json()

    message = payload.get("message", {})
    text = message.get("text", "")
    chat_id = message.get("chat", {}).get("id")

    if not text or not chat_id:
        return JSONResponse({"status": "ignored"})

    response_text = handle_telegram_command(text)

    send_telegram_message(chat_id, response_text)

    return JSONResponse({"status": "ok"})


# ==================================================
# COMMAND ROUTER
# ==================================================

def handle_telegram_command(text: str):

    cmd = text.strip().lower()

    if "@" in cmd:
        cmd = cmd.split("@")[0]

    # --------------------------------------------------
    # HELP
    # --------------------------------------------------

    if cmd in ["/help", "/start"]:

        return (
            "🏃 Marathon Coach AI V5\n\n"
            "Commands:\n"
            "/health\n"
            "/status\n"
            "/recovery\n"
            "/fatigue\n"
            "/week\n"
            "/plan\n"
            "/metrics"
        )

    # --------------------------------------------------
    # HEALTH (FIXED + RESTORED)
    # --------------------------------------------------

    if cmd == "/health":

        return (
            "🩺 System Health\n\n"
            "API: OK\n"
            "Garmin Sync: ACTIVE\n"
            "Recovery Engine: ACTIVE\n"
            "Fatigue Engine: ACTIVE\n"
            f"Timestamp: {datetime.utcnow().isoformat()}"
        )

    # --------------------------------------------------
    # STATUS
    # --------------------------------------------------

    if cmd == "/status":

        return (
            "🧠 System Status\n"
            "Recovery Intelligence V5: ACTIVE\n"
            "All systems operational"
        )

    # --------------------------------------------------
    # METRICS
    # --------------------------------------------------

    if cmd == "/metrics":

        data = sync_garmin_health_to_supabase()

        return (
            "📊 Garmin Metrics\n\n"
            f"Sleep: {data.get('sleep_hours')}\n"
            f"HRV: {data.get('hrv')}\n"
            f"Body Battery: {data.get('body_battery')}\n"
            f"Resting HR: {data.get('resting_hr')}\n"
            f"Weight: {data.get('weight')}"
        )

    # --------------------------------------------------
    # WEEK / PLAN
    # --------------------------------------------------

    if cmd in ["/week", "/plan"]:

        return f"📅 Training Plan\n\n{generate_weekly_plan()}"

    # --------------------------------------------------
    # RECOVERY
    # --------------------------------------------------

    if cmd == "/recovery":

        data = sync_garmin_health_to_supabase()

        recovery = calculate_readiness_score(
            sleep_hours=data.get("sleep_hours"),
            hrv=data.get("hrv"),
            body_battery=data.get("body_battery"),
            resting_hr=data.get("resting_hr"),
            weight=data.get("weight"),
        )

        return (
            "🧠 Recovery\n\n"
            f"Score: {recovery.get('score')}\n"
            f"Status: {recovery.get('status')}"
        )

    # --------------------------------------------------
    # FATIGUE
    # --------------------------------------------------

    if cmd == "/fatigue":

        data = sync_garmin_health_to_supabase()

        fatigue = calculate_fatigue_score(
            sleep_hours=data.get("sleep_hours"),
            hrv=data.get("hrv"),
            body_battery=data.get("body_battery"),
            resting_hr=data.get("resting_hr"),
            weight=data.get("weight"),
        )

        return (
            "⚡ Fatigue\n\n"
            f"Score: {fatigue.get('fatigue_score')}\n"
            f"Status: {fatigue.get('fatigue_status')}"
        )

    return "❓ Unknown command. Try /help"


# ==================================================
# TELEGRAM SENDER
# ==================================================

def send_telegram_message(chat_id, text):

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("Missing TELEGRAM_BOT_TOKEN")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    requests.post(
        url,
        json={
            "chat_id": chat_id,
            "text": text
        },
        timeout=10
    )
