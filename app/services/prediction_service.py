def predict_marathon(metrics):

    weekly_distance = metrics["weekly_distance"]

    average_pace = metrics["average_pace"]

    run_count = metrics["run_count"]

    # -----------------------------------
    # SIMPLE READINESS MODEL
    # -----------------------------------

    readiness_score = min(
        100,
        int(
            (weekly_distance * 1.2)
            + (run_count * 5)
        )
    )

    # -----------------------------------
    # PARSE PACE
    # -----------------------------------

    try:

        minute_part = average_pace.split(":")[0]

        second_part = (
            average_pace
            .split(":")[1]
            .split("/")[0]
        )

        pace_seconds = (
            int(minute_part) * 60
            + int(second_part)
        )

    except:

        return {
            "predicted_time": "N/A",
            "readiness_score": readiness_score,
            "sub4_probability": 0
        }

    # -----------------------------------
    # SIMPLE MARATHON ESTIMATION
    # -----------------------------------

    predicted_seconds = int(
        pace_seconds * 42.195
    )

    hours = predicted_seconds // 3600

    minutes = (
        predicted_seconds % 3600
    ) // 60

    seconds = predicted_seconds % 60

    predicted_time = (
        f"{hours}:{minutes:02d}:{seconds:02d}"
    )

    # -----------------------------------
    # SUB 4 PROBABILITY
    # -----------------------------------

    sub4_probability = 0

    if predicted_seconds < 14400:
        sub4_probability = min(
            95,
            readiness_score
        )

    elif predicted_seconds < 16200:
        sub4_probability = int(
            readiness_score * 0.7
        )

    else:
        sub4_probability = int(
            readiness_score * 0.4
        )

    return {
        "predicted_time": predicted_time,
        "readiness_score": readiness_score,
        "sub4_probability": sub4_probability
    }
