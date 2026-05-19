from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import os
import json
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
# HEALTH CHECK
# ==================================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }


# ==================================================
# GARMIN TEST PIPELINE
# ==================================================

@app.get("/garmin-test")
def garmin_test():

    try:

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

    except Exception as e:

        return {
            "status": "error",
            "message": str(e)
        }


# ==================================================
# WEEK PLAN (JSON SAFE)
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
# PLAN (JSON SAFE)
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
            "recovery": recovery,
            "fatigue": fatigue
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
async def telegram(request: Request):

    try:

        payload = await request.json()

        message = payload.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if not text:

            return JSONResponse({"status": "ignored"})

        response_text = handle_command(text)

        send_telegram(chat_id, response_text)

        return JSONResponse({"status": "ok"})

    except Exception as e:

        return JSONResponse({
            "status": "error",
            "message": str(e)
        })


# ==================================================
# COMMAND HANDLER
# ==================================================

def handle_command(text: str):

    cmd = text.lower().strip()

    # -------------------------
    # STATUS
    # -------------------------

    if cmd == "/status":

        return (
            "🧠 Marathon Coach AI V5\n"
            "Recovery Intelligence: ACTIVE\n"
            "Garmin Sync: ACTIVE\n"
            "Fatigue Engine: ACTIVE"
        )

    # -------------------------
    # WEEK
    # -------------------------

    if cmd == "/week":

        plan = generate_weekly_plan()

        return f"📅 Weekly Plan:\n\n{json.dumps(plan, indent=2)}"

    # -------------------------
    # PLAN
    # -------------------------

    if cmd == "/plan":

        plan = generate_weekly_plan()

        return f"🏃 Plan:\n\n{json.dumps(plan, indent=2)}"

    # -------------------------
    # RECOVERY
    # -------------------------

    if cmd == "/recovery":

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

        return (
            "🧠 Recovery Intelligence V5\n\n"
            f"Recovery Score: {recovery.get('score')}\n"
            f"Status: {recovery.get('status')}\n\n"
            f"Fatigue Score: {fatigue.get('fatigue_score')}\n"
            f"Status: {fatigue.get('fatigue_status')}\n\n"
            f"{fatigue.get('recommendation')}"
        )

    # -------------------------
    # FATIGUE
    # -------------------------

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
            "⚡ Fatigue Report\n\n"
            f"Score: {fatigue.get('fatigue_score')}\n"
            f"Status: {fatigue.get('fatigue_status')}\n\n"
            f"Recommendation:\n{fatigue.get('recommendation')}"
        )

    # -------------------------
    # DEFAULT
    # -------------------------

    return (
        "Unknown command\n\n"
        "/status\n"
        "/week\n"
        "/plan\n"
        "/recovery\n"
        "/fatigue"
    )


# ==================================================
# TELEGRAM SENDER
# ==================================================

def send_telegram(chat_id, text):

    token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not token:
        print("Missing TELEGRAM_BOT_TOKEN")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:

        requests.post(
            url,
            json={
                "chat_id": chat_id,
                "text": text
            },
            timeout=10
        )

    except Exception as e:

        print("Telegram error:", e)
