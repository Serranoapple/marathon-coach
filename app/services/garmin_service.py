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
# FETCH TODAY HEALTH (DEBUG VERSION)
# -----------------------------------

def fetch_today_health():

    client = get_garmin_client()

    today = date.today().isoformat()

    print("TODAY:", today)

    # -----------------------------------
    # SLEEP
    # -----------------------------------

    try:

        sleep_data = client.get_sleep_data(
            today
        )

        print(
            "SLEEP RAW:",
            sleep_data
        )

    except Exception as e:

        print(
            "SLEEP ERROR:",
            e
        )

        sleep_data = {}

    # -----------------------------------
    # HRV
    # -----------------------------------

    try:

        hrv_data = client.get_hrv_data(
            today
        )

        print(
            "HRV RAW:",
            hrv_data
        )

    except Exception as e:

        print(
            "HRV ERROR:",
            e
        )

        hrv_data = {}

    # -----------------------------------
    # BODY BATTERY
    # -----------------------------------

    try:

        body_data = (
            client.get_body_battery(
                today
            )
        )

        print(
            "BODY RAW:",
            body_data
        )

    except Exception as e:

        print(
            "BODY ERROR:",
            e
        )

        body_data = {}

    # -----------------------------------
    # RESTING HR
    # -----------------------------------

    try:

        rhr_data = (
            client.get_rhr_day(
                today
            )
        )

        print(
            "RHR RAW:",
            rhr_data
        )

    except Exception as e:

        print(
            "RHR ERROR:",
            e
        )

        rhr_data = {}

    # -----------------------------------
    # RETURN PLACEHOLDER DATA
    # (indtil vi mapper felterne korrekt)
    # -----------------------------------

    result = {

        "sleep_hours": 0,

        "hrv": None,

        "body_battery": None,

        "resting_hr": None
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
