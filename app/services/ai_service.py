import os
import requests

GROQ_API_KEY = os.getenv("GROQ_API_KEY")


def generate_coaching_feedback(run_data, metrics):

    prompt = f"""
You are an experienced marathon running coach.

The athlete is training for:
Berlin Marathon 2026
Goal: sub 4 hours

Analyze this run and provide short motivational coaching feedback.

RUN:
- Distance: {run_data['distance_km']} km
- Pace: {run_data['pace']}
- Heart rate: {run_data['average_hr']}

WEEKLY METRICS:
- Weekly distance: {metrics['weekly_distance']} km
- Number of runs: {metrics['run_count']}
- Average pace: {metrics['average_pace']}
- Fatigue warning: {metrics['fatigue_warning']}

Keep the response:
- short
- motivating
- practical
- max 4 sentences
"""

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7
        }
    )

    data = response.json()

    print("GROQ RESPONSE:", data)

    return data["choices"][0]["message"]["content"]
