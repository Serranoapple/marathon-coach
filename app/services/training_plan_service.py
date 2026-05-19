# app/services/training_plan_service.py

from datetime import datetime


def generate_weekly_plan():
    """
    Simple Recovery Intelligence V5 training plan generator
    """

    today = datetime.utcnow()

    plan = {
        "week_start": today.strftime("%Y-%m-%d"),
        "goal": "Balanced endurance + recovery",
        "sessions": [
            {
                "day": "Monday",
                "type": "Recovery / Rest",
                "intensity": "low"
            },
            {
                "day": "Tuesday",
                "type": "Easy run",
                "intensity": "zone 2"
            },
            {
                "day": "Wednesday",
                "type": "Strength or rest",
                "intensity": "moderate"
            },
            {
                "day": "Thursday",
                "type": "Tempo run",
                "intensity": "threshold"
            },
            {
                "day": "Friday",
                "type": "Rest",
                "intensity": "low"
            },
            {
                "day": "Saturday",
                "type": "Long run",
                "intensity": "aerobic"
            },
            {
                "day": "Sunday",
                "type": "Recovery run",
                "intensity": "very low"
            }
        ]
    }

    return plan
