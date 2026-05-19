def calculate_readiness_score(
    sleep_hours,
    hrv,
    body_battery,
    resting_hr,
    weight=None
):

    score = 50  # baseline neutral
    status = "UNKNOWN"

    # -----------------------------------
    # SLEEP (meget vigtig)
    # -----------------------------------

    if sleep_hours is not None:

        if sleep_hours >= 8:
            score += 20

        elif sleep_hours >= 7:
            score += 10

        elif sleep_hours >= 6:
            score += 0

        else:
            score -= 15

    # -----------------------------------
    # HRV
    # -----------------------------------

    if hrv is not None:

        if hrv >= 45:
            score += 20

        elif hrv >= 35:
            score += 10

        elif hrv >= 25:
            score += 0

        else:
            score -= 10

    # -----------------------------------
    # BODY BATTERY
    # -----------------------------------

    if body_battery is not None:

        if body_battery >= 70:
            score += 15

        elif body_battery >= 40:
            score += 5

        else:
            score -= 10

    # -----------------------------------
    # RESTING HR
    # -----------------------------------

    if resting_hr is not None:

        if resting_hr <= 50:
            score += 10

        elif resting_hr <= 60:
            score += 5

        else:
            score -= 10

    # -----------------------------------
    # WEIGHT (NY SIGNAL)
    # -----------------------------------

    if weight is not None:

        try:

            w = float(weight)

            # sanity range (meget groft)
            if w < 55 or w > 120:
                score -= 5

            else:
                score += 3  # stabil fysiologisk zone

        except:

            pass

    # -----------------------------------
    # NORMALISER SCORE
    # -----------------------------------

    if score >= 85:
        status = "PEAK"

    elif score >= 70:
        status = "GOOD"

    elif score >= 55:
        status = "MODERATE"

    elif score >= 40:
        status = "LOW"

    else:
        status = "CRITICAL"

    # clamp 0-100
    score = max(0, min(100, score))

    return {
        "score": score,
        "status": status
    }
