import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, filters
import sqlite3

# Bot Settings
TOKEN = "7951716710:AAFBMmwOe_U3Fzf2JnxqXTn9iypkm_6eCTo"
CHANNEL_USERNAME = "@jonnielotter"
ADMIN_ID = 6256195890

# Setup DB
conn = sqlite3.connect("users.db", check_same_thread=False)
c = conn.cursor()
c.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, refer INTEGER, bonus_claimed BOOLEAN DEFAULT 0, balance INTEGER DEFAULT 0)")
conn.commit()

# Logging
logging.basicConfig(level=logging.INFO)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)

    if member.status not in ["member", "creator", "administrator"]:
        keyboard = [[
            InlineKeyboardButton("🔗 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.strip('@')}"),
            InlineKeyboardButton("✅ CHECK", callback_data="checksub")
        ]]
        await update.message.reply_text("🔐 Please join our channel to continue:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        if not c.fetchone():
            c.execute("INSERT INTO users (id, refer, bonus_claimed, balance) VALUES (?, ?, ?, ?)", (user_id, 0, True, 5))
            conn.commit()
            await update.message.reply_text("🎉 You've received ₹5 bonus for joining!
")
        await send_menu(update, context)

# Channel re-check
async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)

    if member.status not in ["member", "creator", "administrator"]:
        await update.callback_query.answer("❌ You're not subscribed!", show_alert=True)
    else:
        c.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        if not c.fetchone():
            c.execute("INSERT INTO users (id, refer, bonus_claimed, balance) VALUES (?, ?, ?, ?)", (user_id, 0, True, 5))
            conn.commit()
            await update.callback_query.message.reply_text("🎉 You've received ₹5 bonus for joining!
")
        await send_menu(update, context)

# Main Menu
async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Balance", callback_data="balance"), InlineKeyboardButton("🎁 Daily Bonus", callback_data="bonus")],
        [InlineKeyboardButton("🔄 Refer & Earn", callback_data="refer"), InlineKeyboardButton("🏦 Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("☎️ Customer Care", callback_data="support")]
    ]
    if update.message:
        await update.message.reply_text("👇 Choose an option", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.callback_query.message.edit_text("👇 Choose an option", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback handler
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if query.data == "balance":
        c.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
        bal = c.fetchone()[0]
        await query.answer()
        await query.edit_message_text(f"💰 Your Balance: ₹{bal}")
    elif query.data == "bonus":
        await query.answer("🎁 Daily bonus coming soon!", show_alert=True)
    elif query.data == "refer":
        await query.answer()
        await query.edit_message_text(f"🔗 Share your referral link:
https://t.me/{context.bot.username}?start={user_id}")
    elif query.data == "withdraw":
        await query.answer()
        await query.edit_message_text("💳 Send your UPI to admin:
📞 PhonePe / GPay / Paytm")
    elif query.data == "support":
        await query.answer()
        await query.edit_message_text("📞 Contact support: @jonnielotter")
    elif query.data == "checksub":
        await check_subscription(update, context)

# Run bot
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle_callback))

print("Bot running...")
app.run_polling()
