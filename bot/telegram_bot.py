import os
import asyncio

print("TELEGRAM_BOT MODULE IMPORTED")

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print("TOKEN FOUND:", TOKEN is not None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🏃 Marathon Coach aktiv"
    )


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Dagens træning kommer senere 🚀"
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "System status:\nCTL: 48\nATL: 55\nTSB: -7"
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start\n"
        "/today\n"
        "/status\n"
        "/help"
    )


async def start_bot():
    print("START_BOT FUNCTION RUNNING")

    print("BUILDING APPLICATION")

    application = (
        Application.builder()
        .token(TOKEN)
        .build()
    )

    print("APPLICATION BUILT")

    application.add_handler(
        CommandHandler("start", start)
    )

    application.add_handler(
        CommandHandler("today", today)
    )

    application.add_handler(
        CommandHandler("status", status)
    )

    application.add_handler(
        CommandHandler("help", help_command)
    )

    print("ENTERING ASYNC CONTEXT")

    async with application:
        print("APPLICATION INITIALIZED")

        await application.start()

        print("APPLICATION STARTED")

        await application.updater.start_polling()

        print("POLLING STARTED")

        while True:
            await asyncio.sleep(3600)
