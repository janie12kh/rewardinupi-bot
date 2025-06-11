
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

TOKEN = "7951716710:AAFBMmwOe_U3Fzf2JnxqXTn9iypkm_6eCTo"
CHANNEL_USERNAME = "@jonnielotter"

users = {}
withdraw_requests = []

logging.basicConfig(level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)

    if member.status in ["member", "creator", "administrator"]:
        users.setdefault(user_id, {"balance": 0, "refer": 0, "bonus_claimed": False})
        keyboard = [
            [InlineKeyboardButton("💰 Balance", callback_data="balance"),
             InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")],
            [InlineKeyboardButton("👥 Refer & Earn", callback_data="refer")],
            [InlineKeyboardButton("📤 Withdraw", callback_data="withdraw")],
            [InlineKeyboardButton("📞 Customer Care", callback_data="support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Welcome to JONNIE LOTTER!", reply_markup=reply_markup)
    else:
        await update.message.reply_text(f"🛡 Please join {CHANNEL_USERNAME} first.")

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = query.data

    if user_id not in users:
        await query.edit_message_text("Please /start first.")
        return

    user = users[user_id]

    if data == "balance":
        await query.edit_message_text(f"💼 Your balance: ₹{user['balance']}")
    elif data == "bonus":
        if user["bonus_claimed"]:
            await query.edit_message_text("🎁 Daily bonus already claimed.")
        else:
            user["balance"] += 2
            user["bonus_claimed"] = True
            await query.edit_message_text("🎉 You claimed ₹2 bonus!")
    elif data == "refer":
        await query.edit_message_text(
            f"👥 Invite friends and earn ₹5 each!
Your referral link:
"
            f"https://t.me/{context.bot.username}?start={user_id}"
        )
    elif data == "withdraw":
        await query.edit_message_text("📤 Send your UPI ID to request withdrawal.")
        context.user_data["awaiting_upi"] = True
    elif data == "support":
        await query.edit_message_text("📞 Contact us: @jonnielotter_support")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if context.user_data.get("awaiting_upi"):
        withdraw_requests.append((user_id, text))
        context.user_data["awaiting_upi"] = False
        await update.message.reply_text("✅ UPI received! We'll review and pay soon.")
    elif update.message.text.startswith("/start"):
        args = update.message.text.split()
        if len(args) > 1:
            ref_id = int(args[1])
            if ref_id != user_id and user_id not in users:
                users.setdefault(ref_id, {"balance": 0, "refer": 0, "bonus_claimed": False})
                users[ref_id]["balance"] += 5
                users[ref_id]["refer"] += 1
        await start(update, context)

def main():
    print("✅ Bot is running...")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
