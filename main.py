import logging, requests, os, asyncio, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, filters, MessageHandler

TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
CHANNEL_ID = "@GMoviesXB"
LOG_CHANNEL_ID = -1004420089406

logging.basicConfig(level=logging.INFO)
started_users = set()

# --- LOGGING ---
async def log_user(update, context):
    user = update.effective_user
    if user.id not in started_users:
        msg = f"👤 **New User:** {user.first_name} (@{user.username}) | ID: `{user.id}`"
        await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=msg, parse_mode='Markdown')
        started_users.add(user.id)

# --- START MENU ---
async def start(update, context):
    await log_user(update, context)
    keyboard = [
        [InlineKeyboardButton("📱 Mobile No Info", callback_data='err')],
        [InlineKeyboardButton("🚗 Vehicle Info", callback_data='err')],
        [InlineKeyboardButton("👤 TG Profile", callback_data='tg_id')],
        [InlineKeyboardButton("📍 Pincode Lookup", callback_data='pin_help')],
        [InlineKeyboardButton("🏦 IFSC Lookup", callback_data='ifsc_help')],
        [InlineKeyboardButton("🎵 YT Downloader", callback_data='yt_help')],
        [InlineKeyboardButton("📁 File to Link", callback_data='file_help')]
    ]
    await update.message.reply_text("✨ **Pro Utility Menu:**", reply_markup=InlineKeyboardMarkup(keyboard))

# --- BUTTON HANDLER ---
async def handle_button(update, context):
    query = update.callback_query
    await query.answer() # Ye command button ko 'click' karne ke liye zaroori hai

    # Force Join Check
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, query.from_user.id)
        if member.status in ['left', 'kicked']:
            return await query.edit_message_text(f"⚠️ 𝑷𝒂𝒉𝒍𝒆 𝑱𝒐𝒊𝒏 𝑲𝒂𝒓 𝑭𝒊𝒓 𝑴𝒂𝒔𝒂𝒍𝒂 𝑴𝒊𝒍𝒆𝒈𝒂: {CHANNEL_ID}")
    except: pass

    # Flat Logic
    if query.data == 'err':
        await query.edit_message_text("🔍 Searching... please wait...")
        await asyncio.sleep(3)
        await query.edit_message_text("❌ 𝑺𝒆𝒓𝒗𝒆𝒓 𝑲𝒊 𝑴𝒂 𝑪𝒉𝒖𝒅𝒊 𝑷𝒂𝒅𝒊 𝑯 𝑩𝒉𝒂𝒊 𝑬𝒏𝒈𝒍𝒊𝒔𝒉 𝑴𝒆 𝑩𝒐𝒍𝒆 𝑻𝒐 𝑺𝒆𝒓𝒗𝒆𝒓 𝑰𝒔𝒔𝒖𝒆𝒔.")
    elif query.data == 'tg_id':
        u = query.from_user
        await query.edit_message_text(f"👤 Name: {u.first_name}\n🆔 ID: `{u.id}`\nUsername: @{u.username}")
    elif query.data == 'pin_help':
        await query.edit_message_text("Type: /pin <pincode>")
    elif query.data == 'ifsc_help':
        await query.edit_message_text("Type: /ifsc <ifsc>")
    elif query.data == 'yt_help':
        await query.edit_message_text("Type: /yt <url>")
    elif query.data == 'file_help':
        await query.edit_message_text("𝑭𝒊𝒍𝒆 𝑲𝒐 𝑭𝒐𝒓𝒘𝒂𝒓𝒅 𝑶𝒓 𝑼𝒑𝒍𝒐𝒂𝒅 𝑲𝒂𝒓𝒐 𝑨𝒃𝒉𝒊 𝑳𝒊𝒏𝒌 𝑩𝒏𝒂 𝑲𝒆 𝑫𝒆𝒕𝒂 𝑯𝒖..")

# --- MAIN ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button)) # Buttons yahan handle ho rahe hain
    
    print("Bot is running...")
    app.run_polling()
        
