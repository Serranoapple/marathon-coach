from fastapi import FastAPI
import asyncio

from bot.telegram_bot import start_bot

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_bot())


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
