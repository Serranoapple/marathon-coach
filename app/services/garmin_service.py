import traceback
from garminconnect import Garmin


# -----------------------------------
# LOGIN / CLIENT (forventes allerede init i dit flow)
# -----------------------------------

def get_garmin_client(username, password):

    try:

        client = Garmin(username, password)
        client.login()
        return client

    except Exception as e:

        print("GARMIN LOGIN ERROR:", e)
        return None


# -----------------------------------
# SLEEP
# -----------------------------------

def get_sleep_data(client):

    try:

        data = client.get_sleep_data()

        daily = data.get("dailySleepDTO", {})

        sleep_seconds = daily.get("sleepTimeSeconds", 0)

        sleep_hours = round(
            sleep_seconds / 3600,
            2
        )

        return sleep_hours

    except Exception as e:

        print("SLEEP ERROR:", e)
        return None


# -----------------------------------
# HRV
# -----------------------------------

def get_hrv(client):

    try:

        data = client.get_hrv_data()

        summary = data.get("hrvSummary", {})

        return summary.get("lastNightAvg")

    except Exception as e:

        print("HRV ERROR:", e)
        return None


# -----------------------------------
# RESTING HEART RATE
# -----------------------------------

def get_resting_hr(client):

    try:

        data = client.get_rhr_data()

        metrics = (
            data.get("allMetrics", {})
            .get("metricsMap", {})
            .get("WELLNESS_RESTING_HEART_RATE", [])
        )

        if not metrics:

            return None

        return metrics[0].get("value")

    except Exception as e:

        print("RHR ERROR:", e)
        return None


# -----------------------------------
# BODY BATTERY
# -----------------------------------

def get_body_battery(client):

    try:

        data = client.get_body_battery()

        values = data.get("bodyBatteryValuesArray", [])

        if not values:

            return None

        return values[-1][1]

    except Exception as e:

        print("BODY BATTERY ERROR:", e)
        return None


# -----------------------------------
# WEIGHT (ROBUST MULTI-FALLBACK)
# -----------------------------------

def get_weight(client):

    try:

        # 1. Body composition endpoint
        try:

            data = client.get_body_composition()

            measurements = (
                data.get("measurementValues")
                or data.get("measurements")
                or []
            )

            if measurements:

                latest = measurements[-1]

                weight = (
                    latest.get("weight")
                    or latest.get("value")
                )

                if weight:

                    weight = float(weight)

                    # grams fallback
                    if weight > 300:
                        weight = weight / 1000

                    return round(weight, 1)

        except Exception as e:

            print("WEIGHT METHOD 1 FAILED:", e)

        # 2. fallback user summary
        try:

            data = client.get_user_summary()

            weight = data.get("weight")

            if weight:

                weight = float(weight)

                return round(weight, 1)

        except Exception as e:

            print("WEIGHT METHOD 2 FAILED:", e)

        return None

    except Exception as e:

        print("WEIGHT ERROR:", e)
        return None


# -----------------------------------
# MAIN SYNC FUNCTION
# -----------------------------------

def sync_garmin_health_to_supabase(supabase):

    try:

        username = supabase.table(
            "settings"
        ).select("*").eq(
            "key",
            "garmin_username"
        ).execute().data[0]["value"]

        password = supabase.table(
            "settings"
        ).select("*").eq(
            "key",
            "garmin_password"
        ).execute().data[0]["value"]

        client = get_garmin_client(
            username,
            password
        )

        if not client:

            return {}

        sleep_hours = get_sleep_data(client)
        hrv = get_hrv(client)
        body_battery = get_body_battery(client)
        resting_hr = get_resting_hr(client)
        weight = get_weight(client)

        print("GARMIN RAW DEBUG:")
        print("sleep:", sleep_hours)
        print("hrv:", hrv)
        print("body_battery:", body_battery)
        print("rhr:", resting_hr)
        print("weight:", weight)

        return {

            "sleep_hours": sleep_hours,
            "hrv": hrv,
            "body_battery": body_battery,
            "resting_hr": resting_hr,
            "weight": weight

        }

    except Exception as e:

        print("SYNC ERROR:", e)
        traceback.print_exc()

        return {}
