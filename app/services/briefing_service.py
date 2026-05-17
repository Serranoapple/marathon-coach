import os
import requests

from app.services.metrics_service import calculate_metrics
from app.services.prediction_service import predict_marathon
from app.services.recovery_service import calculate_recovery_status
from app.services.trend_service import calculate_trend_analysis
from app.services.training_plan_service import generate_training_recommendation


TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def send_daily_briefing(supabase):

    # -----------------------------------
    # CORE DATA
    # -----------------------------------

    metrics = calculate_metrics(supabase)
    prediction = predict_marathon(metrics)
    recovery = calculate_recovery_status(supabase)
    trend = calculate_trend_analysis(supabase)

    recommendation = generate_training_recommendation(
        metrics,
        prediction
    )

    # -----------------------------------
    # BUILD BRIEFING
    # -----------------------------------

    briefing = (
        "🌅 Morning Briefing\n\n"

        "📊 Status\n"
        f"Ugens km: {metrics['weekly_distance']}\n"
        f"Antal løb: {metrics['run_count']}\n"
        f"Gns pace: {metrics['average_pace']}\n\n"

        "🏁 Marathon\n"
        f"Tid: {prediction['predicted_time']}\n"
        f"Readiness: {prediction['readiness_score']}/100\n"
        f"Sub 4 chance: {prediction['sub4_probability']}%\n\n"

        "🩺 Recovery\n"
        f"{recovery['message']}\n\n"

        "📈 Trend\n"
        f"{trend['message']}\n\n"

        "📅 Dagens anbefaling\n"
        f"{recommendation}"
    )

    # -----------------------------------
    # SEND TELEGRAM MESSAGE
    # -----------------------------------

    try:

        requests.post(
            f"https://api.telegram.org/"
            f"bot{TELEGRAM_BOT_TOKEN}/"
            f"sendMessage",
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": briefing
            }
        )

        print("DAILY BRIEFING SENT")

    except Exception as e:

        print("BRIEFING ERROR:", e)
