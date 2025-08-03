from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes
)
import asyncio
import os

TOKEN = os.environ.get("BOT_TOKEN") or "AQUI_VA_TU_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Bienvenido. Envía una foto o video para evitar ser expulsado.")

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    context.chat_data[f"user_{user_id}_verified"] = True

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        user_id = member.id

        await update.message.reply_text(
            f"👀 @{member.username or member.first_name} tiene 60 segundos para enviar una foto o video o será expulsado."
        )

        await asyncio.sleep(60)

        if not context.chat_data.get(f"user_{user_id}_verified"):
            await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=user_id)
            await update.message.reply_text(f"🚫 @{member.username or member.first_name} fue expulsado por no verificar.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))

    app.run_polling()

if __name__ == "__main__":
    main()
