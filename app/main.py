from fastapi import FastAPI
import asyncio

print("MAIN.PY LOADED")

from bot.telegram_bot import start_bot

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    print("FASTAPI STARTUP EVENT RUNNING")

    asyncio.create_task(start_bot())

    print("BOT TASK CREATED")


@app.get("/")
def root():
    return {"status": "running"}


@app.get("/status")
def status():
    return {
        "ctl": 48,
        "atl": 55,
        "tsb": -7
    }
