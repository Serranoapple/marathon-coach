from garminconnect import Garmin
import os
from datetime import date


def get_garmin_client():

    email = os.getenv("peter.boegh.soerensen@gmail.com")
    password = os.getenv("audiaudiA4")

    client = Garmin(email, password)
    client.login()

    return client


def fetch_today_health():

    client = get_garmin_client()

    today = date.today().isoformat()

    data = client.get_stats(today)

    sleep = client.get_sleep_data(today)
    hrv = client.get_hrv_data(today)
    body = client.get_body_battery(today)
    rhr = client.get_rhr_day(today)

    return {
        "sleep_hours": sleep.get("dailySleepDTO", {}).get("sleepTime", 0) / 3600,
        "hrv": hrv.get("hrvValue"),
        "body_battery": body.get("chargedValue"),
        "resting_hr": rhr.get("value")
    }
