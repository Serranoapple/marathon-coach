from fastapi import FastAPI
from services.fitness_engine import get_current_state
from services.ai_coach import get_daily_plan

app = FastAPI()

@app.get("/")
def root():
    return {"status": "Marathon Coach running"}

@app.get("/status")
def status():
    return get_current_state()

@app.get("/today")
def today():
    state = get_current_state()
    plan = get_daily_plan(state)
    return {
        "state": state,
        "plan": plan
    }
