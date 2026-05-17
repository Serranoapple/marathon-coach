def calculate_fitness_score(metrics, recovery, trend):

    # -----------------------------------
    # BASE VALUES
    # -----------------------------------

    weekly_km = metrics["weekly_distance"]
    runs = metrics["run_count"]

    load_ratio = recovery["load_ratio"]
    trend_state = trend["trend"]

    score = 50  # baseline

    # -----------------------------------
    # VOLUME (0–25 point)
    # -----------------------------------

    if 15 <= weekly_km <= 60:
        score += 15
    elif weekly_km > 60:
        score += 20
    elif weekly_km < 10:
        score -= 10

    # -----------------------------------
    # CONSISTENCY (0–15 point)
    # -----------------------------------

    if runs >= 3:
        score += 15
    elif runs == 2:
        score += 8
    else:
        score -= 5

    # -----------------------------------
    # RECOVERY / LOAD (0–25 point)
    # -----------------------------------

    if load_ratio < 1.0:
        score += 25
    elif load_ratio < 1.3:
        score += 10
    elif load_ratio < 1.6:
        score -= 10
    else:
        score -= 25

    # -----------------------------------
    # TREND (0–20 point)
    # -----------------------------------

    if trend_state == "improving":
        score += 20
    elif trend_state == "stable":
        score += 10
    elif trend_state == "declining":
        score -= 15

    # -----------------------------------
    # NORMALIZE
    # -----------------------------------

    score = max(0, min(100, score))

    # -----------------------------------
    # LABEL
    # -----------------------------------

    if score >= 80:
        label = "peak"
        message = "🔥 Topform – klar til hårde pas"
    elif score >= 60:
        label = "good"
        message = "🟢 Stabil form – god progression"
    elif score >= 40:
        label = "medium"
        message = "🟡 Moderat form – fokus på balance"
    else:
        label = "low"
        message = "⚠ Lav form – fokus på restitution"

    return {
        "score": score,
        "label": label,
        "message": message
    }
