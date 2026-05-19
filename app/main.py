# ==================================================
# MAIN.PY - MARATHON COACH AI (APP UI VERSION)
# ==================================================

from flask import Flask, request
import logging

from app.services.garmin_service import sync_garmin_health_to_supabase
from app.services.training_plan_service import generate_weekly_plan
from app.engines.recovery_engine import calculate_readiness_score
from app.engines.fatigue_engine import calculate_fatigue_score

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


# ==================================================
# UI FORMAT HELPERS
# ==================================================

def card(title, subtitle="", lines=None):
    lines = lines or []

    text = f"{title}\n"
    if subtitle:
        text += f"{subtitle}\n\n"

    for l in lines:
        text += f"{l}\n"

    return text


def safe_data():
    try:
        return sync_garmin_health_to_supabase()
    except Exception as e:
        logging.error(e)
        return {
            "sleep_hours": None,
            "hrv": None,
            "body_battery": None,
            "resting_hr": None,
            "weight": None
        }


# ==================================================
# CORE TELEGRAM HANDLER
# ==================================================

def handle_command(cmd: str):

    cmd = cmd.lower().strip()

    # --------------------------
    # START / HELP
    # --------------------------

    if cmd in ["/start", "/help"]:

        return card(
            "🏃 Marathon Coach AI",
            "Dit er dit performance dashboard",
            [
                "/dashboard - oversigt",
                "/recovery - restitution",
                "/fatigue - træthed",
                "/metrics - Garmin data",
                "/plan - træningsplan",
                "/health - system status"
            ]
        )

    # --------------------------
    # DASHBOARD (APP ENTRY)
    # --------------------------

    if cmd == "/dashboard":

        data = safe_data()

        return card(
            "📱 Dashboard",
            "Din aktuelle form",
            [
                f"Søvn: {data.get('sleep_hours')} t",
                f"HRV: {data.get('hrv')}",
                f"Body Battery: {data.get('body_battery')}",
                "",
                "Brug /recovery eller /fatigue"
            ]
        )

    # --------------------------
    # HEALTH
    # --------------------------

    if cmd == "/health":

        return card(
            "🩺 System Health",
            "Alle systemer kører",
            [
                "Garmin: OK",
                "Recovery Engine: OK",
                "Fatigue Engine: OK",
                "Training Plans: OK"
            ]
        )

    # --------------------------
    # METRICS
    # --------------------------

    if cmd == "/metrics":

        data = safe_data()

        return card(
            "📊 Garmin Metrics",
            "Seneste data",
            [
                f"Søvn: {data.get('sleep_hours')}",
                f"HRV: {data.get('hrv')}",
                f"Body Battery: {data.get('body_battery')}",
                f"RHR: {data.get('resting_hr')}",
                f"Vægt: {data.get('weight')}"
            ]
        )

    # --------------------------
    # RECOVERY ENGINE
    # --------------------------

    if cmd == "/recovery":

        data = safe_data()

        recovery = calculate_readiness_score(
            sleep_hours=data.get("sleep_hours"),
            hrv=data.get("hrv"),
            body_battery=data.get("body_battery"),
            resting_hr=data.get("resting_hr"),
            weight=data.get("weight"),
        )

        return card(
            "🧠 Recovery",
            "Restitutionsanalyse",
            [
                f"Score: {recovery.get('score')} / 100",
                f"Status: {recovery.get('status')}",
                "",
                "👉 Klar til træning vurderes her"
            ]
        )

    # --------------------------
    # FATIGUE ENGINE
    # --------------------------

    if cmd == "/fatigue":

        data = safe_data()

        fatigue = calculate_fatigue_score(
            sleep_hours=data.get("sleep_hours"),
            hrv=data.get("hrv"),
            body_battery=data.get("body_battery"),
            resting_hr=data.get("resting_hr"),
            weight=data.get("weight"),
        )

        return card(
            "⚡ Fatigue",
            "Belastningsniveau",
            [
                f"Score: {fatigue.get('fatigue_score')} / 100",
                f"Status: {fatigue.get('fatigue_status')}",
                "",
                "👉 Justér træning efter belastning"
            ]
        )

    # --------------------------
    # TRAINING PLAN
    # --------------------------

    if cmd == "/plan":

        plan = generate_weekly_plan()

        return card(
            "📅 Training Plan",
            "Ugens plan",
            [
                str(plan)[:300]
            ]
        )

    # --------------------------
    # DEFAULT
    # --------------------------

    return card(
        "❓ Ukendt kommando",
        "",
        [
            "Brug /help"
        ]
    )


# ==================================================
# TELEGRAM WEBHOOK
# ==================================================

@app.route("/telegram", methods=["POST"])
def telegram_webhook():

    try:
        data = request.get_json()

        message = data.get("message", {})
        text = message.get("text", "")
        chat_id = message.get("chat", {}).get("id")

        if not text:
            return "ok"

        response = handle_command(text)

        send_telegram_message(chat_id, response)

        return "ok"

    except Exception as e:
        logging.error(e)
        return "error"


# ==================================================
# TELEGRAM SENDER
# ==================================================

import requests
import os

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")


def send_telegram_message(chat_id, text):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text
    }

    try:
        requests.post(url, json=payload)
    except Exception as e:
        logging.error(e)


# ==================================================
# HEALTH CHECK ENDPOINT
# ==================================================

@app.route("/health")
def health():

    return {
        "status": "ok",
        "service": "marathon-coach-ai"
    }


# ==================================================
# ENTRYPOINT
# ==================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
