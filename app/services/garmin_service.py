import logging
from datetime import datetime

from app.engines.recovery_engine import calculate_readiness_score
from app.engines.fatigue_engine import calculate_fatigue_score


# --------------------------------------------------
# SAFE VALUE HELPER
# --------------------------------------------------

def safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


# --------------------------------------------------
# HRV PARSER (robust Garmin format)
# --------------------------------------------------

def extract_hrv(hrv_raw):
    try:
        return hrv_raw.get("hrvSummary", {}).get("weeklyAvg")
    except Exception:
        return None


# --------------------------------------------------
# RESTING HR SAFE EXTRACTION
# --------------------------------------------------

def extract_resting_hr(data):
    try:
        return data.get("restingHeartRate") or data.get("resting_hr")
    except Exception:
        return None


# --------------------------------------------------
# WEIGHT SAFE EXTRACTION
# --------------------------------------------------

def extract_weight(weight_raw):
    try:
        if not weight_raw:
            return None

        avg = weight_raw.get("totalAverage", {})
        return safe_float(avg.get("weight"))
    except Exception:
        return None


# --------------------------------------------------
# MAIN SYNC FUNCTION
# --------------------------------------------------

def sync_garmin_health_to_supabase(supabase=None):
    """
    Fetch + normalize Garmin data + compute recovery + fatigue + store history
    """

    try:
        # --------------------------------------------------
        # PLACEHOLDER: REPLACE WITH YOUR GARMIN CLIENT
        # --------------------------------------------------
        from app.services.garmin_client import GarminClient

        client = GarminClient()

        sleep_data = client.get_sleep_data()
        hrv_data = client.get_hrv_data()
        body_battery = client.get_body_battery()
        weight_data = client.get_weight_data()
        rhr_data = client.get_rhr_data()

        # --------------------------------------------------
        # NORMALIZE VALUES
        # --------------------------------------------------

        sleep_hours = safe_float(sleep_data.get("sleep_hours"))
        hrv = extract_hrv(hrv_data)
        body_battery_val = safe_float(body_battery)
        resting_hr = extract_resting_hr(rhr_data)
        weight = extract_weight(weight_data)

        # --------------------------------------------------
        # ENGINE INPUT
        # --------------------------------------------------

        recovery = calculate_readiness_score(
            sleep_hours=sleep_hours,
            hrv=hrv,
            body_battery=body_battery_val,
            resting_hr=resting_hr,
            weight=weight
        )

        fatigue = calculate_fatigue_score(
            sleep_hours=sleep_hours,
            hrv=hrv,
            body_battery=body_battery_val,
            resting_hr=resting_hr,
            weight=weight
        )

        # --------------------------------------------------
        # SAFE INSERT TO SUPABASE
        # --------------------------------------------------

        if supabase:
            try:
                supabase.table("daily_metrics").insert({
                    "created_at": datetime.utcnow().isoformat(),

                    "sleep_hours": sleep_hours,
                    "hrv": hrv,
                    "body_battery": body_battery_val,
                    "resting_hr": resting_hr,
                    "weight": weight,

                    "recovery_score": recovery.get("score"),
                    "fatigue_score": fatigue.get("score"),
                }).execute()

            except Exception as db_err:
                logging.error(f"Supabase insert error: {db_err}")

        # --------------------------------------------------
        # RETURN CLEAN RESPONSE
        # --------------------------------------------------

        return {
            "sleep_hours": sleep_hours,
            "hrv": hrv,
            "body_battery": body_battery_val,
            "resting_hr": resting_hr,
            "weight": weight,

            "recovery": recovery,
            "fatigue": fatigue
        }

    except Exception as e:
        logging.error(f"Garmin sync failed: {e}")

        return {
            "sleep_hours": None,
            "hrv": None,
            "body_battery": None,
            "resting_hr": None,
            "weight": None,

            "recovery": {"score": 0, "status": "ERROR"},
            "fatigue": {"score": 0, "status": "ERROR"}
        }
