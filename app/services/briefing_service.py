import os
import requests

from app.services.metrics_service import calculate_metrics
from app.services.prediction_service import predict_marathon
from app.services.ai_service import generate_coaching_feedback

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_daily_briefing(supabase):

    metrics = calculate_metrics(supabase)

    prediction = predict_marathon(metrics)

    run_data = {
        "distance_km": metrics["weekly_distance"],
        "pace": metrics["average_pace"],
        "average_hr": "N/A"
    }

    try:

        ai_feedback = generate_coaching_feedback(
            run_data,
            metrics
        )

    except:

        ai_feedback = (
            "Stabil træning anbefales i dag."
        )

    briefing = (
        f"🌅 Morning Briefing\n\n"
        f"📊 Ugens km: {metrics['weekly_distance']}\n"
        f"🏃 Antal løb: {metrics['run_count']}\n"
        f"⚡ Readiness: {prediction['readiness_score']}/100\n"
        f"🏁 Marathon prediction: "
        f"{prediction['predicted_time']}\n\n"
        f"🤖 Coach\n"
        f"{ai_feedback}"
    )

    requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": briefing
        }
    )

    print("DAILY BRIEFING SENT")
