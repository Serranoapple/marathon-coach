from garminconnect import Garmin
from datetime import date
import os


# -----------------------------------
# GARMIN LOGIN
# -----------------------------------

def get_garmin_client():

    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    print("GARMIN LOGIN START")

    client = Garmin(
        email,
        password
    )

    client.login()

    print("GARMIN LOGIN SUCCESS")

    return client


# -----------------------------------
# FETCH TODAY HEALTH
# -----------------------------------

def fetch_today_health():

    client = get_garmin_client()

    today = date.today().isoformat()

    print("TODAY:", today)

    # -----------------------------------
    # FETCH RAW DATA
    # -----------------------------------

    sleep_data = client.get_sleep_data(
        today
    )

    print(
        "SLEEP RAW:",
        sleep_data
    )

    hrv_data = client.get_hrv_data(
        today
    )

    print(
        "HRV RAW:",
        hrv_data
    )

    body_data = client.get_body_battery(
        today
    )

    print(
        "BODY RAW:",
        body_data
    )

    rhr_data = client.get_rhr_day(
        today
    )

    print(
        "RHR RAW:",
        rhr_data
    )

    # -----------------------------------
    # PARSE SLEEP
    # -----------------------------------

    try:

        sleep_seconds = (
            sleep_data
            .get("dailySleepDTO", {})
            .get("sleepTimeSeconds", 0)
        )

        sleep_hours = round(
            sleep_seconds / 3600,
            1
        )

    except Exception as e:

        print(
            "SLEEP PARSE ERROR:",
            e
        )

        sleep_hours = None

    # -----------------------------------
    # PARSE HRV
    # -----------------------------------

    try:

        hrv = (
            hrv_data
            .get("hrvSummary", {})
            .get("lastNightAvg")
        )

    except Exception as e:

        print(
            "HRV PARSE ERROR:",
            e
        )

        hrv = None

    # -----------------------------------
    # PARSE BODY BATTERY
    # -----------------------------------

    try:

        body_battery = (
            body_data[0]
            .get("charged")
        )

    except Exception as e:

        print(
            "BODY BATTERY PARSE ERROR:",
            e
        )

        body_battery = None

    # -----------------------------------
    # PARSE RESTING HR
    # -----------------------------------

    try:

        resting_hr = (
            rhr_data
            .get("allMetrics", {})
            .get("metricsMap", {})
            .get(
                "WELLNESS_RESTING_HEART_RATE",
                [{}]
            )[0]
            .get("value")
        )

    except Exception as e:

        print(
            "RHR PARSE ERROR:",
            e
        )

        resting_hr = None

    # -----------------------------------
    # FINAL RESULT
    # -----------------------------------

    result = {

        "sleep_hours":
        sleep_hours,

        "hrv":
        hrv,

        "body_battery":
        body_battery,

        "resting_hr":
        resting_hr
    }

    print(
        "FINAL HEALTH RESULT:",
        result
    )

    return result


# -----------------------------------
# SYNC TO SUPABASE
# -----------------------------------

def sync_garmin_health_to_supabase(
    supabase
):

    try:

        print(
            "GARMIN SYNC START"
        )

        data = fetch_today_health()

        print(
            "INSERTING TO SUPABASE:",
            data
        )

        response = (
            supabase
            .table("health_metrics")
            .insert(data)
            .execute()
        )

        print(
            "SUPABASE RESPONSE:",
            response
        )

        print(
            "GARMIN SYNC SUCCESS"
        )

        return data

    except Exception as e:

        print(
            "GARMIN SYNC ERROR:",
            e
        )

        return {
            "error": str(e)
        }
