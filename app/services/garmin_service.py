from garminconnect import Garmin
from datetime import datetime
import os


def sync_garmin_health_to_supabase(supabase):

    print("STARTING GARMIN SYNC")

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

        sleep_data = client.get_sleep_data(
            today.isoformat()
        )

        print("SLEEP RAW:", sleep_data)

        sleep_ms = (
            sleep_data
            .get("dailySleepDTO", {})
            .get("sleepTimeSeconds")
        )

        if sleep_ms:

            sleep_hours = round(
                sleep_ms / 3600,
                2
            )

    except Exception as e:

        print("SLEEP ERROR:", e)

    # --------------------------------------------------
    # HRV
    # --------------------------------------------------

    hrv = None

    try:

        hrv_data = client.get_hrv_data(
            today.isoformat()
        )

        print("HRV RAW:", hrv_data)

        hrv = (
            hrv_data
            .get("hrvSummary", {})
            .get("lastNightAvg")
        )

    except Exception as e:

        print("HRV ERROR:", e)

    # --------------------------------------------------
    # BODY BATTERY
    # --------------------------------------------------

    body_battery = None

    try:

        body_data = client.get_body_battery(
            today.isoformat()
        )

        print("BODY RAW:", body_data)

        if isinstance(body_data, list) and len(body_data) > 0:

            latest = body_data[-1]

            body_battery = latest.get("charged")

    except Exception as e:

        print("BODY BATTERY ERROR:", e)

    # --------------------------------------------------
    # RESTING HEART RATE
    # --------------------------------------------------

    resting_hr = None

    try:

        rhr_data = client.get_rhr_day_values(
            today.isoformat()
        )

        print("RHR RAW:", rhr_data)

        metrics = (
            rhr_data
            .get("allMetrics", {})
            .get("metricsMap", {})
            .get("WELLNESS_RESTING_HEART_RATE", [])
        )

        if metrics:

            resting_hr = metrics[-1].get("value")

    except Exception as e:

        print("RHR ERROR:", e)

    # --------------------------------------------------
    # WEIGHT (FIXED)
    # --------------------------------------------------

    weight = None

    try:

        weight_data = client.get_body_composition(
            today.isoformat()
        )

        print("WEIGHT RAW:", weight_data)

        if (
            weight_data
            and isinstance(weight_data, list)
            and len(weight_data) > 0
        ):

            latest = weight_data[-1]

            raw_weight = latest.get("weight")

            if raw_weight is not None:

                # Garmin returns grams → kg
                weight = round(
                    raw_weight / 1000,
                    1
                )

    except Exception as e:

        print("WEIGHT ERROR:", e)

    # --------------------------------------------------
    # UPSERT SUPABASE
    # --------------------------------------------------

    try:

        supabase.table("health_metrics").upsert({

            "date": today.isoformat(),

            "sleep_hours": sleep_hours,
            "hrv": hrv,
            "body_battery": body_battery,
            "resting_hr": resting_hr,
            "weight": weight

        }).execute()

        print("GARMIN SYNC COMPLETE")

    except Exception as e:

        print("SUPABASE ERROR:", e)

    # --------------------------------------------------
    # RETURN FOR TESTING
    # --------------------------------------------------

    return {

        "sleep_hours": sleep_hours,
        "hrv": hrv,
        "body_battery": body_battery,
        "resting_hr": resting_hr,
        "weight": weight
    }
