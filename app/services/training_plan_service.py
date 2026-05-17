def generate_training_recommendation(
    metrics,
    prediction
):

    weekly_distance = (
        metrics["weekly_distance"]
    )

    fatigue = (
        metrics["fatigue_warning"]
    )

    readiness = (
        prediction["readiness_score"]
    )

    # -----------------------------------
    # FATIGUE PRIORITY
    # -----------------------------------

    if fatigue:

        return (
            "⚠ Høj belastning registreret.\n"
            "Anbefaling: restitutionsdag "
            "eller meget roligt Zone 2 pas."
        )

    # -----------------------------------
    # LOW TRAINING LOAD
    # -----------------------------------

    if weekly_distance < 15:

        return (
            "🏃 Lav ugentlig volumen.\n"
            "Anbefaling: 5-8 km roligt løb "
            "for at bygge base."
        )

    # -----------------------------------
    # BUILDING PHASE
    # -----------------------------------

    if readiness < 40:

        return (
            "📈 Baseopbygning i fokus.\n"
            "Anbefaling: roligt Zone 2 "
            "med fokus på kontinuitet."
        )

    # -----------------------------------
    # IMPROVING FITNESS
    # -----------------------------------

    if readiness < 70:

        return (
            "🔥 Formen udvikler sig.\n"
            "Anbefaling: tempo-pas "
            "eller længere roligt pas."
        )

    # -----------------------------------
    # HIGH READINESS
    # -----------------------------------

    return (
        "🏁 Høj readiness.\n"
        "Anbefaling: marathon-specifikt "
        "tempo eller langtur."
    )
