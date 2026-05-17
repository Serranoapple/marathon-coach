from datetime import datetime, timedelta


def calculate_recovery_status(
    supabase
):

    today = datetime.utcnow()

    seven_days_ago = (
        today - timedelta(days=7)
    )

    twentyeight_days_ago = (
        today - timedelta(days=28)
    )

    # -----------------------------------
    # FETCH RUNS
    # -----------------------------------

    response = (
        supabase
        .table("runs")
        .select("*")
        .execute()
    )

    runs = response.data

    acute_load = 0
    chronic_load = 0

    # -----------------------------------
    # LOAD CALCULATION
    # -----------------------------------

    for run in runs:

        try:

            run_date = datetime.fromisoformat(
                run["created_at"]
                .replace("Z", "+00:00")
            )

            distance = float(
                run["distance_km"]
            )

            # 7 DAYS
            if run_date >= seven_days_ago:

                acute_load += distance

            # 28 DAYS
            if run_date >= twentyeight_days_ago:

                chronic_load += distance

        except:

            continue

    # -----------------------------------
    # NORMALIZE CHRONIC
    # -----------------------------------

    chronic_weekly_average = (
        chronic_load / 4
    )

    # -----------------------------------
    # FATIGUE RATIO
    # -----------------------------------

    if chronic_weekly_average > 0:

        load_ratio = (
            acute_load /
            chronic_weekly_average
        )

    else:

        load_ratio = 1

    # -----------------------------------
    # STATUS
    # -----------------------------------

    if load_ratio > 1.5:

        status = "high"

        message = (
            "⚠ Høj belastning.\n"
            "Øget risiko for overtræning."
        )

    elif load_ratio > 1.2:

        status = "moderate"

        message = (
            "🟡 Moderat belastning.\n"
            "Prioritér restitution."
        )

    else:

        status = "good"

        message = (
            "🟢 God balance mellem "
            "træning og restitution."
        )

    return {
        "acute_load": round(
            acute_load,
            1
        ),
        "chronic_load": round(
            chronic_weekly_average,
            1
        ),
        "load_ratio": round(
            load_ratio,
            2
        ),
        "status": status,
        "message": message
    }
