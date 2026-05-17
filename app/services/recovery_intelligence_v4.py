def calculate_recovery_intelligence_v4(
    health,
    recovery,
    fitness,
    trend
):

    score = 50
    reasons = []

    # -----------------------------------
    # SLEEP
    # -----------------------------------

    sleep = health.get("sleep_hours")

    if sleep is not None:

        if sleep >= 8:
            score += 20

        elif sleep >= 7:
            score += 10

        elif sleep < 6:
            score -= 25
            reasons.append("Lav søvn")

    # -----------------------------------
    # HRV
    # -----------------------------------

    hrv = health.get("hrv")

    if hrv is not None:

        if hrv >= 70:
            score += 20

        elif hrv < 45:
            score -= 25
            reasons.append("Lav HRV")

    # -----------------------------------
    # BODY BATTERY
    # -----------------------------------

    body = health.get("body_battery")

    if body is not None:

        if body >= 80:
            score += 15

        elif body < 40:
            score -= 15
            reasons.append("Lav energi (Body Battery)")

    # -----------------------------------
    # RESTING HR
    # -----------------------------------

    rhr = health.get("resting_hr")

    if rhr is not None:

        if rhr > 60:
            score -= 10
            reasons.append("Høj hvilepuls")

    # -----------------------------------
    # LOAD RATIO
    # -----------------------------------

    load_ratio = recovery.get("load_ratio")

    if load_ratio > 1.5:
        score -= 20
        reasons.append("Høj træningsbelastning")

    elif load_ratio < 0.8:
        score += 10

    # -----------------------------------
    # TREND
    # -----------------------------------

    if trend.get("trend") == "declining":
        score -= 15
        reasons.append("Negativ formtrend")

    elif trend.get("trend") == "improving":
        score += 10

    # -----------------------------------
    # FITNESS BONUS
    # -----------------------------------

    fitness_score = fitness.get("score")

    if fitness_score > 80:
        score += 10

    elif fitness_score < 40:
        score -= 10

    # -----------------------------------
    # NORMALIZE
    # -----------------------------------

    score = max(0, min(100, score))

    # -----------------------------------
    # STATUS
    # -----------------------------------

    if score >= 80:
        status = "peak"
        message = "🔥 Du er klar til hård træning"

    elif score >= 60:
        status = "good"
        message = "🟢 God træningsklarhed"

    elif score >= 40:
        status = "moderate"
        message = "🟡 Reducér intensitet"

    else:
        status = "poor"
        message = "⚠ Hvile anbefales"

    return {
        "score": score,
        "status": status,
        "message": message,
        "reasons": reasons
    }
