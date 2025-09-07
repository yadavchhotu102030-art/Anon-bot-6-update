import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)
from telegram.error import Forbidden, BadRequest, TimedOut

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
SPECTATOR_GROUP_ID = os.getenv("SPECTATOR_GROUP_ID")

waiting_users = []
active_chats = {}
banned_users = set()
seen_users = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id in banned_users:
        await update.message.reply_text("🚫 You are banned from using this bot.")
        return

    # Log new user identity (only once)
    if user.id not in seen_users:
        seen_users.add(user.id)
        if SPECTATOR_GROUP_ID:
            name = user.full_name or "(no name)"
            username = f"@{user.username}" if user.username else "(none)"
            msg = (
                "🆕 New User Started\n"
                f"👤 Name: {name}\n"
                f"🔗 Username: {username}\n"
                f"🆔 ID: {user.id}"
            )
            try:
                await context.bot.send_message(int(SPECTATOR_GROUP_ID), msg)
            except Exception as e:
                logger.warning(f"Spectator new user log error: {e}")

    keyboard = [
        [InlineKeyboardButton("🤝 Start Chatting", callback_data="find_partner")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")]
    ]
    await update.message.reply_text(
        "👋 Welcome to Anonymous Chat Bot!\nClick below to start chatting:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "find_partner":
        user_id = query.from_user.id
        if user_id in waiting_users:
            await query.message.reply_text("⏳ You are already waiting for a partner...")
            return
        if waiting_users:
            partner_id = waiting_users.pop(0)
            active_chats[user_id] = partner_id
            active_chats[partner_id] = user_id
            await context.bot.send_message(user_id, "🤝 You are now connected!")
            await context.bot.send_message(partner_id, "🤝 You are now connected!")
        else:
            waiting_users.append(user_id)
            await query.message.reply_text("🔎 Searching for a partner...")
    elif query.data == "help":
        await query.message.reply_text("ℹ️ Just click 'Start Chatting' to find a partner! Use /stop to end.")

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in banned_users:
        return

    if user_id not in active_chats:
        await update.message.reply_text("❌ You are not in a chat. Click 'Start Chatting'.")
        return

    partner_id = active_chats[user_id]
    try:
        await context.bot.copy_message(partner_id, user_id, update.message.message_id)
    except (Forbidden, BadRequest, TimedOut) as e:
        logger.warning(f"Ignored error while forwarding: {e}")
    except Exception as e:
        logger.error(f"Critical error: {e}")
        if SPECTATOR_GROUP_ID:
            try:
                await context.bot.send_message(int(SPECTATOR_GROUP_ID), f"⚠️ Critical error: {e}")
            except:
                pass

    if SPECTATOR_GROUP_ID:
        text_preview = update.message.text or "[non-text message]"
        try:
            await context.bot.send_message(
                int(SPECTATOR_GROUP_ID),
                f"👁 {user_id} → {partner_id}\n💬 {text_preview}"
            )
        except Exception as e:
            logger.warning(f"Spectator forward error: {e}")

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        active_chats.pop(partner_id, None)
        await context.bot.send_message(user_id, "🛑 Chat ended.")
        await context.bot.send_message(partner_id, "🛑 Your partner left.")

        if SPECTATOR_GROUP_ID:
            try:
                await context.bot.send_message(
                    int(SPECTATOR_GROUP_ID),
                    f"🚪 User {user_id} ended chat with User {partner_id}"
                )
            except Exception as e:
                logger.warning(f"Spectator chat end error: {e}")
    else:
        await update.message.reply_text("❌ You are not chatting.")

async def getid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    await update.message.reply_text(f"📌 This group ID is: `{chat.id}`")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("getid", getid))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, message_handler))
    logger.info("Bot started...")
    app.run_polling()

if __name__ == "__main__":
    main()
