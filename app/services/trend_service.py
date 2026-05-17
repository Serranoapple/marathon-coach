from datetime import datetime, timedelta


def calculate_trend_analysis(
    supabase
):

    response = (
        supabase
        .table("runs")
        .select("*")
        .execute()
    )

    runs = response.data

    today = datetime.utcnow()

    last_14_days = (
        today - timedelta(days=14)
    )

    previous_14_days = (
        today - timedelta(days=28)
    )

    recent_runs = []
    older_runs = []

    # -----------------------------------
    # SPLIT PERIODS
    # -----------------------------------

    for run in runs:

        try:

            run_date = datetime.fromisoformat(
                run["created_at"]
                .replace("Z", "+00:00")
            )

            if run_date >= last_14_days:

                recent_runs.append(run)

            elif run_date >= previous_14_days:

                older_runs.append(run)

        except:

            continue

    # -----------------------------------
    # DISTANCE
    # -----------------------------------

    recent_distance = sum(
        float(r["distance_km"])
        for r in recent_runs
    )

    older_distance = sum(
        float(r["distance_km"])
        for r in older_runs
    )

    # -----------------------------------
    # RUN COUNTS
    # -----------------------------------

    recent_count = len(recent_runs)
    older_count = len(older_runs)

    # -----------------------------------
    # PACE COMPARISON
    # -----------------------------------

    def pace_to_seconds(pace):

        try:

            value = pace.replace(
                "/km",
                ""
            )

            minutes, seconds = (
                value.split(":")
            )

            return (
                int(minutes) * 60
                + int(seconds)
            )

        except:

            return None

    recent_paces = []

    for run in recent_runs:

        p = pace_to_seconds(
            run.get("pace", "")
        )

        if p:

            recent_paces.append(p)

    older_paces = []

    for run in older_runs:

        p = pace_to_seconds(
            run.get("pace", "")
        )

        if p:

            older_paces.append(p)

    recent_avg_pace = (
        sum(recent_paces) /
        len(recent_paces)
        if recent_paces
        else None
    )

    older_avg_pace = (
        sum(older_paces) /
        len(older_paces)
        if older_paces
        else None
    )

    # -----------------------------------
    # TREND STATUS
    # -----------------------------------

    trend = "stable"

    message = (
        "📊 Stabil udvikling."
    )

    if (
        recent_distance >
        older_distance * 1.15
    ):

        trend = "improving"

        message = (
            "📈 Træningsvolumen "
            "er stigende."
        )

    if (
        recent_avg_pace
        and older_avg_pace
        and recent_avg_pace
        < older_avg_pace
    ):

        improvement = int(
            older_avg_pace
            - recent_avg_pace
        )

        trend = "improving"

        message = (
            f"🚀 Pace forbedret "
            f"med {improvement} sek/km "
            f"de sidste 14 dage."
        )

    if (
        recent_distance <
        older_distance * 0.8
    ):

        trend = "declining"

        message = (
            "⚠ Træningsvolumen "
            "er faldende."
        )

    return {
        "trend": trend,
        "recent_distance": round(
            recent_distance,
            1
        ),
        "older_distance": round(
            older_distance,
            1
        ),
        "recent_runs": recent_count,
        "older_runs": older_count,
        "message": message
    }
