from garminconnect import Garmin
from datetime import date
import os


# -----------------------------------
# LOGIN
# -----------------------------------

def get_garmin_client():

    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    client = Garmin(email, password)

    client.login()

    return client


# -----------------------------------
# FETCH TODAY HEALTH
# -----------------------------------

def fetch_today_health():

    client = get_garmin_client()

    today = date.today().isoformat()

    # -------------------------------
    # SLEEP
    # -------------------------------

    sleep_data = client.get_sleep_data(today)

    sleep_seconds = (
        sleep_data
        .get("dailySleepDTO", {})
        .get("sleepTime", 0)
    )

    sleep_hours = round(
        sleep_seconds / 3600,
        1
    )

    # -------------------------------
    # HRV
    # -------------------------------

    try:

        hrv_data = client.get_hrv_data(today)

        hrv = hrv_data.get(
            "hrvValue"
        )

    except:

        hrv = None

    # -------------------------------
    # BODY BATTERY
    # -------------------------------

    try:

        body_data = (
            client.get_body_battery(today)
        )

        body_battery = (
            body_data.get("chargedValue")
        )

    except:

        body_battery = None

    # -------------------------------
    # RESTING HR
    # -------------------------------

    try:

        rhr_data = (
            client.get_rhr_day(today)
        )

        resting_hr = (
            rhr_data.get("value")
        )

    except:

        resting_hr = None

    return {

        "sleep_hours":
        sleep_hours,

        "hrv":
        hrv,

        "body_battery":
        body_battery,

        "resting_hr":
        resting_hr
    }


# -----------------------------------
# SYNC TO SUPABASE
# -----------------------------------

def sync_garmin_health_to_supabase(
    supabase
):

    try:

        data = fetch_today_health()

        supabase.table(
            "health_metrics"
        ).insert(data).execute()

        print(
            "GARMIN SYNC SUCCESS"
        )

        print(data)

        return data

    except Exception as e:

        print(
            "GARMIN SYNC ERROR:",
            e
        )

        return None
