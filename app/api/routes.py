from flask import Blueprint, jsonify
import logging

from app.services.garmin_service import sync_garmin_health_to_supabase
from app.engines.recovery_engine import calculate_readiness_score
from app.engines.fatigue_engine import calculate_fatigue_score
from app.services.training_plan_service import generate_weekly_plan

api_bp = Blueprint("api", __name__)


# --------------------------------------------------
# SAFE DATA WRAPPER
# --------------------------------------------------

def get_data(supabase=None):
    try:
        return sync_garmin_health_to_supabase(supabase)
    except Exception as e:
        logging.error(f"Garmin error: {e}")
        return {
            "sleep_hours": None,
            "hrv": None,
            "body_battery": None,
            "resting_hr": None,
            "weight": None
        }


# --------------------------------------------------
# DASHBOARD (MAIN VIEW)
# --------------------------------------------------

@api_bp.route("/dashboard")
def dashboard():

    data = get_data()

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

    return jsonify({
        "sleep_hours": data.get("sleep_hours"),
        "hrv": data.get("hrv"),
        "body_battery": data.get("body_battery"),
        "resting_hr": data.get("resting_hr"),
        "weight": data.get("weight"),

        "recovery": recovery,
        "fatigue": fatigue
    })


# --------------------------------------------------
# RECOVERY ONLY
# --------------------------------------------------

@api_bp.route("/recovery")
def recovery():

    data = get_data()

    result = calculate_readiness_score(
        sleep_hours=data.get("sleep_hours"),
        hrv=data.get("hrv"),
        body_battery=data.get("body_battery"),
        resting_hr=data.get("resting_hr"),
        weight=data.get("weight"),
    )

    return jsonify(result)


# --------------------------------------------------
# FATIGUE ONLY
# --------------------------------------------------

@api_bp.route("/fatigue")
def fatigue():

    data = get_data()

    result = calculate_fatigue_score(
        sleep_hours=data.get("sleep_hours"),
        hrv=data.get("hrv"),
        body_battery=data.get("body_battery"),
        resting_hr=data.get("resting_hr"),
        weight=data.get("weight"),
    )

    return jsonify(result)


# --------------------------------------------------
# METRICS (RAW GARMIN DATA)
# --------------------------------------------------

@api_bp.route("/metrics")
def metrics():

    data = get_data()

    return jsonify(data)


# --------------------------------------------------
# WEEKLY PLAN
# --------------------------------------------------

@api_bp.route("/plan")
def plan():

    result = generate_weekly_plan()

    return jsonify({
        "plan": result
    })


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@api_bp.route("/health")
def health():

    return jsonify({
        "status": "ok",
        "api": "active",
        "engines": ["recovery", "fatigue", "plan"]
    })
