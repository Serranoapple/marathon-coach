from garminconnect import Garmin
from datetime import datetime
import os


def sync_garmin_health_to_supabase(supabase):

    print("🚀 START GARMIN SYNC")

    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")

    client = Garmin(email, password)
    client.login()

    today = datetime.utcnow().date()

    # --------------------------------------------------
    # SLEEP
    # --------------------------------------------------

    sleep_hours = None

    try:

        sleep_data = client.get_sleep_data(today.isoformat())

        print("SLEEP RAW:", sleep_data)

        sleep_sec = (
            sleep_data
            .get("dailySleepDTO", {})
            .get("sleepTimeSeconds")
        )

        if sleep_sec:

            sleep_hours = round(sleep_sec / 3600, 2)

    except Exception as e:

        print("SLEEP ERROR:", e)

    # --------------------------------------------------
    # HRV
    # --------------------------------------------------

    hrv = None

    try:

        hrv_data = client.get_hrv_data(today.isoformat())

        print("HRV RAW:", hrv_data)

        hrv = (
            hrv_data
            .get("hrvSummary", {})
            .get("lastNightAvg")
        )

        if hrv is not None:

            hrv = int(hrv)

    except Exception as e:

        print("HRV ERROR:", e)

    # --------------------------------------------------
    # BODY BATTERY
    # --------------------------------------------------

    body_battery = None

    try:

        body_data = client.get_body_battery(today.isoformat())

        print("BODY RAW:", body_data)

        if isinstance(body_data, list) and len(body_data) > 0:

            latest = body_data[-1]

            body_battery = latest.get("charged")

            if body_battery is not None:

                body_battery = int(body_battery)

    except Exception as e:

        print("BODY BATTERY ERROR:", e)

    # --------------------------------------------------
    # RESTING HEART RATE
    # --------------------------------------------------

    resting_hr = None

    try:

        summary = client.get_stats(today.isoformat())

        print("SUMMARY RAW:", summary)

        resting_hr = summary.get("restingHeartRate")

        if resting_hr is not None:

            resting_hr = int(resting_hr)

    except Exception as e:

        print("RHR ERROR:", e)

    # --------------------------------------------------
    # WEIGHT
    # --------------------------------------------------

    weight = None

    try:

        weight_data = client.get_body_composition(today.isoformat())

        print("WEIGHT RAW:", weight_data)

        date_weight_list = weight_data.get("dateWeightList", [])

        if len(date_weight_list) > 0:

            latest = date_weight_list[-1]

            raw_weight = latest.get("weight")

            if raw_weight:

                weight = round(raw_weight / 1000, 1)

    except Exception as e:

        print("WEIGHT ERROR:", e)

    # --------------------------------------------------
    # SAVE TO SUPABASE
    # --------------------------------------------------

    try:

        payload = {

            "date": today.isoformat(),
            "sleep_hours": sleep_hours,
            "hrv": hrv,
            "body_battery": body_battery,
            "resting_hr": resting_hr,
            "weight": weight

        }

        print("SUPABASE PAYLOAD:", payload)

        supabase.table("health_metrics").upsert(payload).execute()

        print("✅ GARMIN SYNC COMPLETE")

    except Exception as e:

        print("SUPABASE ERROR:", e)

    # --------------------------------------------------
    # RETURN TEST DATA
    # --------------------------------------------------

    return {

        "sleep_hours": sleep_hours,
        "hrv": hrv,
        "body_battery": body_battery,
        "resting_hr": resting_hr,
        "weight": weight
    }
