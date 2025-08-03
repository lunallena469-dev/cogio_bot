import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, MessageHandler, filters, ContextTypes
import asyncio

# Token del bot (REEMPLAZA si cambias de bot)
TOKEN = "8075777545:AAFaoOeTcf-z6SuB69TTjMwZOjrgLoGV1tg"

# Diccionario para rastrear usuarios nuevos y sus tareas de espera
pending_users = {}

# Configuración del logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def check_user_timeout(user_id, chat_id, app):
    await asyncio.sleep(60)
    if user_id in pending_users:
        try:
            await app.ban_chat_member(chat_id, user_id)
            await app.unban_chat_member(chat_id, user_id)  # Para permitir que regresen manualmente
            logging.info(f"Expulsado {user_id} por no enviar foto/video")
        except Exception as e:
            logging.error(f"Error al expulsar usuario: {e}")
        del pending_users[user_id]

async def handle_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.chat_member.new_chat_members:
        user_id = member.id
        chat_id = update.chat_member.chat.id
        pending_users[user_id] = chat_id
        asyncio.create_task(check_user_timeout(user_id, chat_id, context.application))

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in pending_users:
        del pending_users[user_id]
        logging.info(f"Usuario {user_id} cumplió con enviar media")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    # Maneja cuando un nuevo miembro se une
    app.add_handler(ChatMemberHandler(handle_new_member, ChatMemberHandler.CHAT_MEMBER))

    # Maneja si el nuevo usuario envía una foto o video
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_media))

    logging.info("Bot iniciado...")
    app.run_polling()
