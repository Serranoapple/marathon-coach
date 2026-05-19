def generate_weekly_plan(
    metrics,
    readiness,
    recovery_v4
):

    readiness_score = readiness.get(
        "score",
        0
    )

    weekly_distance = metrics.get(
        "weekly_distance",
        0
    )

    if readiness_score < 40:

        return (
            "Recovery Week\n\n"

            "Mon: Rest\n"
            "Tue: 5 km easy\n"
            "Wed: Mobility\n"
            "Thu: 6 km easy\n"
            "Fri: Rest\n"
            "Sat: 8 km easy\n"
            "Sun: Walk"
        )

    if weekly_distance < 20:

        return (
            "Base Building Week\n\n"

            "Mon: Rest\n"
            "Tue: 8 km easy\n"
            "Wed: Strength\n"
            "Thu: 10 km aerobic\n"
            "Fri: Rest\n"
            "Sat: 14 km long run\n"
            "Sun: Recovery jog"
        )

    return (
        "Performance Week\n\n"

        "Mon: Recovery\n"
        "Tue: Intervals\n"
        "Wed: Easy run\n"
        "Thu: Tempo\n"
        "Fri: Rest\n"
        "Sat: Long run\n"
        "Sun: Recovery"
    )
