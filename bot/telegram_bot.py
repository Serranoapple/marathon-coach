import os

print("TELEGRAM BOT MODULE IMPORTED")

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print("TOKEN FOUND:", TOKEN is not None)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏃 Marathon Coach aktiv")


async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Dagens træning kommer senere 🚀")


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("CTL: 48 | ATL: 55 | TSB: -7")


def start_bot_sync():
    print("START_BOT_SYNC RUNNING")
    print("BUILDING APPLICATION")

    application = Application.builder().token(TOKEN).build()

    print("APPLICATION BUILT")

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("today", today))
    application.add_handler(CommandHandler("status", status))

    print("STARTING POLLING (BLOCKING)")

    application.run_polling()
