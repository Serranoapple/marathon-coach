def generate_training_recommendation(
    metrics,
    readiness,
    recovery_v4
):

    weekly_distance = metrics.get(
        "weekly_distance",
        0
    )

    readiness_score = readiness.get(
        "score",
        0
    )

    recovery_score = recovery_v4.get(
        "score",
        0
    )

    run_count = metrics.get(
        "run_count",
        0
    )

    # --------------------------------------------------
    # VERY LOW RECOVERY
    # --------------------------------------------------

    if readiness_score < 40:

        return (
            "Recovery focused day.\n\n"

            "• 30-45 min walk\n"
            "• Mobility work\n"
            "• Hydration focus\n"
            "• Prioritize sleep"
        )

    # --------------------------------------------------
    # LOW RECOVERY
    # --------------------------------------------------

    if readiness_score < 60:

        return (
            "Easy aerobic session.\n\n"

            "• 5-8 km zone 2\n"
            "• Relaxed pace\n"
            "• No intensity today\n"
            "• Optional stretching"
        )

    # --------------------------------------------------
    # BUILD BASE
    # --------------------------------------------------

    if weekly_distance < 20:

        return (
            "Aerobic base session.\n\n"

            "• 8-12 km easy\n"
            "• Comfortable effort\n"
            "• Add 4 x strides\n"
            "• Focus on consistency"
        )

    # --------------------------------------------------
    # HIGH READINESS
    # --------------------------------------------------

    if recovery_score > 75:

        return (
            "Quality workout recommended.\n\n"

            "• Tempo intervals\n"
            "• Marathon pace blocks\n"
            "• Strong aerobic effort\n"
            "• Good day for progression"
        )

    # --------------------------------------------------
    # DEFAULT
    # --------------------------------------------------

    return (
        "Steady endurance training.\n\n"

        "• Moderate aerobic run\n"
        "• Controlled heart rate\n"
        "• Maintain rhythm\n"
        "• Recovery optimized"
    )
