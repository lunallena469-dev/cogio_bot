import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ChatMemberHandler, MessageHandler, ContextTypes, filters
import asyncio
from datetime import datetime, timedelta

TOKEN = os.getenv('TOKEN')
logging.basicConfig(level=logging.INFO)
pending_users = {}

async def countdown_messages(context: ContextTypes.DEFAULT_TYPE, chat_id: int, user_id: int):
    tiempos = [60, 45, 30, 15]
    for t in tiempos:
        if user_id not in pending_users:
            break
        await context.bot.send_message(chat_id, f"⏳ Tiempo restante: {t} segundos...")
        await asyncio.sleep(15)
    if user_id in pending_users:
        await context.bot.send_message(chat_id, f"❌ Tiempo agotado. Expulsando al usuario...")

async def new_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    member = update.chat_member
    user = member.new_chat_member.user
    chat = update.effective_chat

    if member.new_chat_member.status == 'member':
        logging.info(f"Nuevo usuario: {user.full_name}")

        await context.bot.send_message(
            chat.id,
            (
                f"👋 Bienvenido, {user.mention_html()}!\n\n"
                "📸 Por seguridad del grupo, debes enviar una **foto o video tuyo real** dentro de los próximos 60 segundos.\n"
                "⏳ Si no lo haces, serás expulsado automáticamente."
            ),
            parse_mode='HTML'
        )

        deadline = datetime.now() + timedelta(seconds=60)
        pending_users[user.id] = {'chat_id': chat.id, 'deadline': deadline}
        asyncio.create_task(countdown_messages(context, chat.id, user.id))
        await asyncio.sleep(60)

        if user.id in pending_users:
            try:
                await context.bot.ban_chat_member(chat.id, user.id)
                await context.bot.unban_chat_member(chat.id, user.id)
                logging.info(f"{user.full_name} expulsado por no enviar foto/video.")
            except Exception as e:
                logging.error(f"Error al expulsar a {user.full_name}: {e}")
            del pending_users[user.id]

async def media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in pending_users:
        del pending_users[user.id]
        await update.message.reply_text("✅ ¡Gracias! Verificación completada. Bienvenido.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(ChatMemberHandler(new_member_handler, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, media_handler))
    print("Bot ejecutándose...")
    app.run_polling()

if __name__ == '__main__':
    main()
