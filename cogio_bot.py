from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
import asyncio

TOKEN = "AQUI_VA_TU_TOKEN"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hola! Envía una foto o video en 60 segundos o serás expulsado.")

async def check_new_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Bienvenido {member.mention_html()}! Por favor envía una foto o video en 60 segundos.",
            parse_mode="HTML"
        )
        await asyncio.sleep(60)

        history = await context.bot.get_chat_history(update.effective_chat.id, limit=100)
        found = False
        for msg in history:
            if msg.from_user.id == member.id and (msg.photo or msg.video):
                found = True
                break
        if not found:
            await context.bot.ban_chat_member(update.effective_chat.id, member.id)
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f"{member.full_name} ha sido expulsado por no enviar foto o video.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, check_new_member))
    app.run_polling()

if __name__ == "__main__":
    main()
