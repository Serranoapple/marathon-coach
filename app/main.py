from fastapi import FastAPI
import threading

print("MAIN.PY LOADED")

from bot.telegram_bot import start_bot_sync

app = FastAPI()


@app.on_event("startup")
def startup_event():
    print("FASTAPI STARTUP EVENT RUNNING")

    # Start Telegram bot i separat thread (blocking-safe)
    bot_thread = threading.Thread(target=start_bot_sync)
    bot_thread.daemon = True
    bot_thread.start()

    print("BOT THREAD STARTED")


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
