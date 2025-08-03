from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
import asyncio

TOKEN = "8075777545:AAFaoOeTcf-z6SuB69TTjMwZOjrgLoGV1tg"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola, envíame una foto o video dentro de 60 segundos o serás expulsado.")


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        user_id = member.id
        chat_id = update.effective_chat.id

        # Mensaje de advertencia
        await update.message.reply_text(f"{member.full_name}, tienes 60 segundos para enviar una foto o video o serás expulsado.")

        # Espera 60 segundos
        await asyncio.sleep(60)

        # Verifica si el usuario envió una foto o video
        if user_id not in context.chat_data:
            await context.bot.ban_chat_member(chat_id=chat_id, user_id=user_id)
            await context.bot.send_message(chat_id=chat_id, text=f"{member.full_name} fue expulsado por no enviar foto/video.")
        else:
            del context.chat_data[user_id]


async def handle_photo_or_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    context.chat_data[user_id] = True


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_photo_or_video))

    app.run_polling()


if __name__ == "__main__":
    main()
