import random

# --- MOCK STATE (indtil Strava kommer) ---
mock_data = {
    "ctl": 48,
    "atl": 55,
    "weekly_km": 28,
    "last_run": "8 km easy",
}

def get_current_state():
    ctl = mock_data["ctl"]
    atl = mock_data["atl"]

    tsb = ctl - atl

    return {
        "ctl": ctl,
        "atl": atl,
        "tsb": tsb,
        "weekly_km": mock_data["weekly_km"],
        "last_run": mock_data["last_run"],
        "fatigue_level": "high" if tsb < -10 else "normal"
    }
