import logging
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    filters,
)

import os

TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

PHOTO_OR_VIDEO_TIMEOUT = 60  # tiempo de espera en segundos
AUTHORIZED_USERS = set()


async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        chat_id = update.effective_chat.id
        user_id = member.id

        # Notificar y agregar a lista temporal
        await update.message.reply_text(
            f"Hola {member.full_name}, por favor envía una foto o video en los próximos {PHOTO_OR_VIDEO_TIMEOUT} segundos o serás expulsado del grupo."
        )

        # Esperar
        await asyncio.sleep(PHOTO_OR_VIDEO_TIMEOUT)

        # Si no se autorizó, expulsar
        if user_id not in AUTHORIZED_USERS:
            try:
                await context.bot.ban_chat_member(chat_id, user_id)
                await context.bot.unban_chat_member(chat_id, user_id)
                await context.bot.send_message(chat_id, f"{member.full_name} fue expulsado por no enviar foto/video.")
            except Exception as e:
                logging.error(f"Error expulsando a {member.full_name}: {e}")
        else:
            AUTHORIZED_USERS.discard(user_id)


async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    AUTHORIZED_USERS.add(user_id)


def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_member))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

    app.run_polling()


if __name__ == "__main__":
    main()
