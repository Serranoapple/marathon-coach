from flask import Blueprint, jsonify, request

from app.services.garmin_service import sync_garmin_health_to_supabase
from app.engines.recovery_engine import calculate_readiness_score
from app.engines.fatigue_engine import calculate_fatigue_score

# NOTE:
# supabase client bør initieres ét sted (fx app/core/supabase_client.py)
from app.core.supabase_client import supabase


api_bp = Blueprint("api", __name__)


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@api_bp.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "service": "marathon-coach",
        "version": "v5"
    })


# --------------------------------------------------
# DASHBOARD (LIVE DATA)
# --------------------------------------------------

@api_bp.route("/dashboard")
def dashboard():

    try:
        data = sync_garmin_health_to_supabase(supabase)

        return jsonify({
            "sleep_hours": data.get("sleep_hours"),
            "hrv": data.get("hrv"),
            "body_battery": data.get("body_battery"),
            "resting_hr": data.get("resting_hr"),
            "weight": data.get("weight"),

            "recovery": data.get("recovery"),
            "fatigue": data.get("fatigue")
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --------------------------------------------------
# HISTORY (STEP 3A - REAL TRENDS)
# --------------------------------------------------

@api_bp.route("/history")
def history():

    try:
        rows = (
            supabase.table("daily_metrics")
            .select("*")
            .order("created_at", desc=False)
            .limit(30)
            .execute()
        )

        return jsonify(rows.data)

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# --------------------------------------------------
# MANUAL SYNC (OPTIONAL DEBUG)
# --------------------------------------------------

@api_bp.route("/sync", methods=["POST"])
def sync():

    try:
        result = sync_garmin_health_to_supabase(supabase)

        return jsonify({
            "status": "success",
            "data": result
        })

    except Exception as e:

        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
