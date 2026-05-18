def calculate_readiness_score(
    sleep_hours,
    hrv,
    body_battery,
    resting_hr
):

    score = 50

    # -----------------------------------
    # SLEEP
    # -----------------------------------

    if sleep_hours:

        if sleep_hours >= 8:
            score += 20

        elif sleep_hours >= 7:
            score += 15

        elif sleep_hours >= 6:
            score += 5

        else:
            score -= 10

    # -----------------------------------
    # HRV
    # -----------------------------------

    if hrv:

        if hrv >= 40:
            score += 20

        elif hrv >= 30:
            score += 10

        elif hrv >= 20:
            score += 0

        else:
            score -= 10

    # -----------------------------------
    # BODY BATTERY
    # -----------------------------------

    if body_battery:

        if body_battery >= 80:
            score += 20

        elif body_battery >= 60:
            score += 10

        elif body_battery >= 40:
            score += 0

        else:
            score -= 15

    # -----------------------------------
    # RESTING HR
    # -----------------------------------

    if resting_hr:

        if resting_hr <= 50:
            score += 10

        elif resting_hr <= 55:
            score += 5

        elif resting_hr >= 65:
            score -= 10

    # -----------------------------------
    # LIMITS
    # -----------------------------------

    score = max(
        0,
        min(score, 100)
    )

    # -----------------------------------
    # STATUS
    # -----------------------------------

    if score >= 85:

        status = "Peak Readiness"

    elif score >= 70:

        status = "Good Recovery"

    elif score >= 50:

        status = "Moderate Fatigue"

    else:

        status = "Recovery Needed"

    return {

        "score": score,

        "status": status
    }
