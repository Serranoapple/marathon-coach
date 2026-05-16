from datetime import datetime, timedelta


def calculate_metrics(supabase):

    # sidste 7 dage
    seven_days_ago = (
        datetime.utcnow() - timedelta(days=7)
    ).isoformat()

    response = supabase.table("runs") \
        .select("*") \
        .gte("created_at", seven_days_ago) \
        .execute()

    runs = response.data

    if not runs:
        return {
            "weekly_distance": 0,
            "run_count": 0,
            "average_pace": "N/A",
            "fatigue_warning": False
        }

    # -----------------------------------
    # WEEKLY DISTANCE
    # -----------------------------------

    total_distance = sum(
        run["distance_km"] for run in runs
    )

    # -----------------------------------
    # RUN COUNT
    # -----------------------------------

    run_count = len(runs)

    # -----------------------------------
    # AVERAGE PACE
    # -----------------------------------

    total_seconds = 0

    for run in runs:

        pace = run.get("pace")

        if pace and ":" in pace:

            minute_part = pace.split(":")[0]
            second_part = pace.split(":")[1].split("/")[0]

            seconds = (
                int(minute_part) * 60
                + int(second_part)
            )

            total_seconds += seconds

    avg_seconds = total_seconds / run_count

    avg_minutes = int(avg_seconds // 60)
    avg_remaining_seconds = int(avg_seconds % 60)

    average_pace = (
        f"{avg_minutes}:{avg_remaining_seconds:02d}/km"
    )

    # -----------------------------------
    # SIMPLE FATIGUE DETECTION
    # -----------------------------------

    fatigue_warning = total_distance > 50

    return {
        "weekly_distance": round(total_distance, 2),
        "run_count": run_count,
        "average_pace": average_pace,
        "fatigue_warning": fatigue_warning
    }
