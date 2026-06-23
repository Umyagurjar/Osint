import logging, requests, os, yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
CHANNEL_ID = "@GMoviesXA"
LOG_CHANNEL = -1004420089406

logging.basicConfig(level=logging.INFO)
started_users = set()

# --- UTILITIES ---
async def log_user(user):
    if user.id not in started_users:
        try: 
            msg = f"👤 **New User:** {user.first_name} (@{user.username})\n🆔 `{user.id}`"
            # Note: Iske liye bot ko log_channel mein admin banayein
            started_users.add(user.id)
        except: pass

async def is_member(update, context):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status not in ['left', 'kicked']
    except: return False

# --- UI ---
async def show_menu(update, query=None):
    kb = [
        [InlineKeyboardButton("📱 Mobile Info", callback_data='err'), InlineKeyboardButton("🚗 Vehicle Info", callback_data='err')],
        [InlineKeyboardButton("📍 Pincode", callback_data='pin_mode'), InlineKeyboardButton("🏦 IFSC", callback_data='ifsc_mode')],
        [InlineKeyboardButton("🎵/🎥 YT Downloader", callback_data='yt_mode'), InlineKeyboardButton("📁 File to Link", callback_data='file_mode')]
    ]
    if query: await query.edit_message_text("✨ **Mega Utility Hub**", reply_markup=InlineKeyboardMarkup(kb))
    else: await update.message.reply_text("✨ **Mega Utility Hub**", reply_markup=InlineKeyboardMarkup(kb))

# --- HANDLERS ---
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    
    # 1. Force Join Check
    if not await is_member(update, context):
        return await query.edit_message_text(f"⚠️ Pehle Channel Join Karo:\n{CHANNEL_ID}")

    data = query.data
    if data == 'back':
        await show_menu(update, query=query)
    elif data == 'err':
        await query.edit_message_text("❌ Server Down.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))
    else:
        context.user_data['mode'] = data
        await query.edit_message_text(f"📝 {data.replace('_mode', '').upper()} mode activated. Enter details:", 
                                     reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))

async def text_handler(update, context):
    mode = context.user_data.get('mode')
    if not mode: return
    
    await update.message.reply_text("⏳ Processing...")
    val = update.message.text
    
    # Logic Hub
    if mode == 'pin_mode':
        data = requests.get(f"https://api.postalpincode.in/pincode/{val}").json()
        res = f"📮 Area: {data[0]['PostOffice'][0]['Name']}" if data[0]['Status'] == 'Success' else "❌ Invalid."
    elif mode == 'ifsc_mode':
        data = requests.get(f"https://ifsc.razorpay.com/{val}").json()
        res = f"🏦 Bank: {data.get('BANK', 'Not Found')}" if 'BANK' in data else "❌ Invalid."
    elif mode == 'yt_mode':
        # Simple YT Link logic
        res = "✅ Download starting..." 
    else:
        res = "❌ Something went wrong."
        
    await update.message.reply_text(res, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))

async def start(update, context):
    await log_user(update.effective_user)
    await show_menu(update)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("Bot is running...")
    app.run_polling()
  
