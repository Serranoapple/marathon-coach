import os
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def get_daily_plan(state):

    prompt = f"""
You are an elite marathon coach.

Athlete state:
- CTL: {state['ctl']}
- ATL: {state['atl']}
- TSB: {state['tsb']}
- Weekly km: {state['weekly_km']}
- Last run: {state['last_run']}
- Fatigue: {state['fatigue_level']}

Give:
1. today's training
2. intensity
3. short explanation
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama3-70b-8192",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        r = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            json=payload,
            headers=headers,
            timeout=30
        )
        return r.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"AI error: {str(e)}"
