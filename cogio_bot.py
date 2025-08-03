import asyncio
import logging
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder, 
    ChatMemberHandler, 
    MessageHandler, 
    filters, 
    ContextTypes
)

# Reemplaza tu token aquí
TOKEN = "8075777545:AAFaoOeTcf-z6SuB69TTjMwZOjrgLoGV1tg"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

new_users_pending = {}

async def restrict_user(chat_id, user_id, context):
    try:
        await context.bot.restrict_chat_member(
            chat_id, user_id,
            permissions=ChatPermissions(can_send_messages=False)
        )
    except Exception as e:
        logging.error(f"Restrict error: {e}")

async def kick_user(chat_id, user_id, context):
    try:
        await context.bot.ban_chat_member(chat_id, user_id)
        await context.bot.unban_chat_member(chat_id, user_id)
        logging.info(f"User {user_id} kicked from chat {chat_id}")
    except Exception as e:
        logging.error(f"Kick error: {e}")

async def handle_new_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.chat_member.new_chat_members:
        user_id = member.id
        chat_id = update.chat_member.chat.id

        # Restringe al nuevo miembro
        await restrict_user(chat_id, user_id, context)

        # Espera 60 segundos
        await asyncio.sleep(60)

        # Si no envió foto/video, lo expulsa
        if user_id in new_users_pending:
            await kick_user(chat_id, user_id, context)
            del new_users_pending[user_id]

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if update.message.photo or update.message.video:
        try:
            # Permite al usuario hablar si ya envió media
            await context.bot.restrict_chat_member(
                chat_id, user_id,
                permissions=ChatPermissions(
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            if user_id in new_users_pending:
                del new_users_pending[user_id]
        except Exception as e:
            logging.error(f"Media permit error: {e}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(ChatMemberHandler(handle_new_chat_member, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

    app.run_polling()

if __name__ == '__main__':
    main()
