import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)

from telegram_bot.handlers import start, handle_message

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# Load token securely
TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TOKEN:
    raise EnvironmentError("❌ TELEGRAM_TOKEN is not set in environment variables.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Sorry, I didn’t understand that command.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))  # catch unknown commands

    print("🤖 Bot is running... Press CTRL+C to stop.")
    app.run_polling()

if __name__ == "__main__":
    main()
