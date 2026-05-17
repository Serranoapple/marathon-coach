def generate_weekly_plan(
    metrics,
    recovery,
    fitness,
    trend
):

    weekly_km = metrics["weekly_distance"]
    load_ratio = recovery["load_ratio"]
    fitness_score = fitness["score"]
    trend_state = trend["trend"]

    plan = []

    # -----------------------------------
    # LOAD ADJUSTMENT
    # -----------------------------------

    if load_ratio > 1.5:
        intensity = "low"
    elif load_ratio > 1.2:
        intensity = "moderate"
    else:
        intensity = "normal"

    # -----------------------------------
    # FITNESS ADJUSTMENT
    # -----------------------------------

    if fitness_score > 75:
        volume_factor = 1.2
    elif fitness_score > 50:
        volume_factor = 1.0
    else:
        volume_factor = 0.8

    base_long_run = int(12 * volume_factor)

    # -----------------------------------
    # PLAN STRUCTURE
    # -----------------------------------

    if intensity == "low":

        plan = [
            "Mandag: Hvile",
            "Tirsdag: 5 km meget let",
            "Onsdag: hvile",
            "Torsdag: 5 km let",
            "Fredag: hvile",
            f"Lørdag: {base_long_run} km rolig tur",
            "Søndag: recovery jog 4 km"
        ]

    elif intensity == "moderate":

        plan = [
            "Mandag: hvile",
            "Tirsdag: 6 km let",
            "Onsdag: interval 4x3 min",
            "Torsdag: 5 km recovery",
            "Fredag: hvile",
            f"Lørdag: {base_long_run + 2} km lang tur",
            "Søndag: 5 km rolig"
        ]

    else:

        plan = [
            "Mandag: hvile",
            "Tirsdag: 7 km let",
            "Onsdag: interval 6x3 min",
            "Torsdag: 6 km rolig",
            "Fredag: tempo 5 km",
            f"Lørdag: {base_long_run + 4} km lang tur",
            "Søndag: 6 km recovery"
        ]

    # -----------------------------------
    # TREND MODIFIER
    # -----------------------------------

    if trend_state == "declining":

        plan.append(
            "⚠ Reducer intensitet hvis træthed"
        )

    if trend_state == "improving":

        plan.append(
            "🚀 God progression – hold struktur"
        )

    return {
        "intensity": intensity,
        "plan": plan
    }
