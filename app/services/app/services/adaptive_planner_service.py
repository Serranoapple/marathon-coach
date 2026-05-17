from datetime import datetime


def generate_daily_adaptive_plan(
    metrics,
    recovery,
    trend,
    fitness,
    prediction
):

    today = datetime.utcnow().strftime("%A")

    load_ratio = recovery["load_ratio"]
    fitness_score = fitness["score"]
    trend_state = trend["trend"]
    readiness = prediction["readiness_score"]

    # -----------------------------------
    # DEFAULT
    # -----------------------------------

    workout = "6 km rolig tur"
    intensity = "normal"

    # -----------------------------------
    # RECOVERY LOGIC
    # -----------------------------------

    if load_ratio > 1.5:

        workout = "Hvile eller 30 min gang"
        intensity = "recovery"

    elif load_ratio > 1.3:

        workout = "5 km recovery run"
        intensity = "low"

    # -----------------------------------
    # FITNESS LOGIC
    # -----------------------------------

    elif fitness_score > 80 and readiness > 75:

        workout = "Interval: 6x3 min hårdt"
        intensity = "high"

    elif fitness_score > 65:

        workout = "8 km steady run"
        intensity = "moderate"

    # -----------------------------------
    # TREND LOGIC
    # -----------------------------------

    if trend_state == "declining":

        workout += "\n⚠ Fokus på restitution"

    elif trend_state == "improving":

        workout += "\n🚀 God progression"

    # -----------------------------------
    # DAY MODIFIER
    # -----------------------------------

    if today == "Sunday":

        workout = "Lang rolig tur 12-18 km"

    if today == "Monday":

        workout = "Recovery / mobilitet"

    return {
        "day": today,
        "workout": workout,
        "intensity": intensity
    }
