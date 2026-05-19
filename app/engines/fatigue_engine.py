from datetime import datetime


def calculate_fatigue_score(
    sleep_hours,
    hrv,
    body_battery,
    resting_hr,
    weight=None,
):

    fatigue = 0

    explanations = []

    # --------------------------------------------------
    # SLEEP ANALYSIS
    # --------------------------------------------------

    if sleep_hours is not None:

        if sleep_hours < 5:

            fatigue += 35
            explanations.append("Very low sleep")

        elif sleep_hours < 6:

            fatigue += 25
            explanations.append("Low sleep")

        elif sleep_hours < 7:

            fatigue += 15
            explanations.append("Moderate sleep debt")

        elif sleep_hours >= 8:

            fatigue -= 5
            explanations.append("Good sleep recovery")

    # --------------------------------------------------
    # HRV ANALYSIS
    # --------------------------------------------------

    if hrv is not None:

        if hrv < 20:

            fatigue += 30
            explanations.append("HRV severely suppressed")

        elif hrv < 25:

            fatigue += 20
            explanations.append("HRV suppressed")

        elif hrv < 30:

            fatigue += 10
            explanations.append("HRV slightly reduced")

        elif hrv >= 40:

            fatigue -= 5
            explanations.append("Strong HRV")

    # --------------------------------------------------
    # BODY BATTERY
    # --------------------------------------------------

    if body_battery is not None:

        if body_battery < 20:

            fatigue += 30
            explanations.append("Body Battery critically low")

        elif body_battery < 40:

            fatigue += 20
            explanations.append("Body Battery low")

        elif body_battery < 60:

            fatigue += 10
            explanations.append("Body Battery moderate")

        elif body_battery >= 80:

            fatigue -= 5
            explanations.append("Body Battery well recovered")

    # --------------------------------------------------
    # RESTING HEART RATE
    # --------------------------------------------------

    if resting_hr is not None:

        if resting_hr >= 65:

            fatigue += 25
            explanations.append("Resting HR elevated")

        elif resting_hr >= 58:

            fatigue += 15
            explanations.append("Resting HR slightly elevated")

        elif resting_hr <= 50:

            fatigue -= 5
            explanations.append("Resting HR optimal")

    # --------------------------------------------------
    # WEIGHT FLUCTUATION PLACEHOLDER
    # --------------------------------------------------

    if weight is not None:

        # Future hydration logic placeholder
        explanations.append(f"Weight tracked: {weight} kg")

    # --------------------------------------------------
    # CLAMP SCORE
    # --------------------------------------------------

    fatigue = max(0, min(100, fatigue))

    # --------------------------------------------------
    # FATIGUE STATUS
    # --------------------------------------------------

    if fatigue <= 20:

        status = "FRESH"

    elif fatigue <= 40:

        status = "LOW FATIGUE"

    elif fatigue <= 60:

        status = "MODERATE FATIGUE"

    elif fatigue <= 80:

        status = "HIGH FATIGUE"

    else:

        status = "OVERLOADED"

    # --------------------------------------------------
    # TRAINING RECOMMENDATION
    # --------------------------------------------------

    if fatigue <= 20:

        recommendation = (
            "High intensity training acceptable"
        )

    elif fatigue <= 40:

        recommendation = (
            "Normal training acceptable"
        )

    elif fatigue <= 60:

        recommendation = (
            "Moderate training recommended"
        )

    elif fatigue <= 80:

        recommendation = (
            "Recovery focused training advised"
        )

    else:

        recommendation = (
            "Rest day strongly recommended"
        )

    # --------------------------------------------------
    # RETURN
    # --------------------------------------------------

    return {

        "fatigue_score": fatigue,
        "fatigue_status": status,
        "recommendation": recommendation,
        "explanations": explanations,
        "generated_at": datetime.utcnow().isoformat()

    }
