import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from services.fitness_engine import get_current_state
from services.ai_coach import get_daily_plan

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

print("=== TELEGRAM BOT FILE LOADED ===")
print("TOKEN FOUND:", TOKEN is not None)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🏃 Marathon Coach aktiv")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_current_state()
    await update.message.reply_text(str(state))

async def today(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_current_state()
    plan = get_daily_plan(state)
    await update.message.reply_text(plan)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("today", today))

    print("=== STARTING POLLING ===")
    app.run_polling()

if __name__ == "__main__":
    main()
