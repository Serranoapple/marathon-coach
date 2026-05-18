from garminconnect import Garmin
from datetime import date
import os


# -----------------------------------
# GARMIN CLIENT
# -----------------------------------

def get_garmin_client():

    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    if not email or not password:
        raise Exception("Missing GARMIN credentials")

    print("GARMIN LOGIN START")

    client = Garmin(email, password)
    client.login()

    print("GARMIN LOGIN SUCCESS")

    return client


# -----------------------------------
# FETCH RAW DATA
# -----------------------------------

def fetch_garmin_raw():

    client = get_garmin_client()

    today = date.today().isoformat()

    print("TODAY:", today)

    sleep = client.get_sleep_data(today)
    hrv = client.get_hrv_data(today)
    body = client.get_body_battery(today)
    rhr = client.get_rhr_day(today)

    return sleep, hrv, body, rhr


# -----------------------------------
# PARSE SLEEP
# -----------------------------------

def parse_sleep(sleep):

    try:

        seconds = (
            sleep
            .get("dailySleepDTO", {})
            .get("sleepTimeSeconds", 0)
        )

        return round(seconds / 3600, 1)

    except Exception as e:

        print("SLEEP PARSE ERROR:", e)

        return None


# -----------------------------------
# PARSE HRV
# -----------------------------------

def parse_hrv(hrv):

    try:

        return (
            hrv
            .get("hrvSummary", {})
            .get("lastNightAvg")
        )

    except Exception as e:

        print("HRV PARSE ERROR:", e)

        return None


# -----------------------------------
# PARSE BODY BATTERY
# -----------------------------------

def parse_body_battery(body):

    try:

        if isinstance(body, list) and len(body) > 0:

            return body[0].get("charged")

        return None

    except Exception as e:

        print("BODY BATTERY PARSE ERROR:", e)

        return None


# -----------------------------------
# PARSE RESTING HR
# -----------------------------------

def parse_resting_hr(rhr):

    try:

        return (
            rhr
            .get("allMetrics", {})
            .get("metricsMap", {})
            .get(
                "WELLNESS_RESTING_HEART_RATE",
                [{}]
            )[0]
            .get("value")
        )

    except Exception as e:

        print("RHR PARSE ERROR:", e)

        return None


# -----------------------------------
# MAIN NORMALIZED OUTPUT
# -----------------------------------

def get_garmin_health():

    sleep, hrv, body, rhr = fetch_garmin_raw()

    result = {

        "sleep_hours":
            parse_sleep(sleep),

        "hrv":
            parse_hrv(hrv),

        "body_battery":
            parse_body_battery(body),

        "resting_hr":
            parse_resting_hr(rhr)
    }

    print("GARMIN FINAL RESULT:", result)

    return result


# -----------------------------------
# SYNC TO SUPABASE (SAFE TYPES)
# -----------------------------------

def sync_garmin_health_to_supabase(supabase):

    try:

        print("GARMIN SYNC START")

        data = get_garmin_health()

        # -----------------------------------
        # TYPE SAFETY LAYER (IMPORTANT)
        # -----------------------------------

        cleaned = {

            "sleep_hours":
                float(data["sleep_hours"])
                if data["sleep_hours"] is not None else None,

            "hrv":
                int(float(data["hrv"]))
                if data["hrv"] is not None else None,

            "body_battery":
                int(float(data["body_battery"]))
                if data["body_battery"] is not None else None,

            "resting_hr":
                int(float(data["resting_hr"]))
                if data["resting_hr"] is not None else None
        }

        print("INSERT CLEAN DATA:", cleaned)

        response = (
            supabase
            .table("health_metrics")
            .insert(cleaned)
            .execute()
        )

        print("SUPABASE RESPONSE:", response)

        return cleaned

    except Exception as e:

        print("GARMIN SYNC ERROR:", e)

        return {
            "error": str(e)
        }
