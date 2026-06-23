import logging, requests, os, asyncio, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, filters, MessageHandler

TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
CHANNEL_ID = "@GMoviesXB"
LOG_CHANNEL_ID = -1004420089406
PHOTO_URL = "https://graph.org/file/5ab741a9acc297d3df19e-48744a8755ad7e02b0.jpg"

logging.basicConfig(level=logging.INFO)

# User-start tracking set
started_users = set()

# --- 1. LOGGING (Single Time) ---
async def log_user(update):
    user = update.effective_user
    if user.id not in started_users:
        msg = f"👤 **New Unique User:** {user.first_name} (@{user.username})\nID: `{user.id}`"
        await update.get_bot().send_message(chat_id=LOG_CHANNEL_ID, text=msg, parse_mode='Markdown')
        started_users.add(user.id)

# --- 2. FLAT MENU ---
async def start(update, context):
    await log_user(update)
    keyboard = [
        [InlineKeyboardButton("📱 Mobile Info", callback_data='err')],
        [InlineKeyboardButton("🚗 Vehicle Info", callback_data='err')],
        [InlineKeyboardButton("👤 TG Profile", callback_data='tg_id')],
        [InlineKeyboardButton("📍 Pincode Lookup", callback_data='pin_help')],
        [InlineKeyboardButton("🏦 IFSC Lookup", callback_data='ifsc_help')],
        [InlineKeyboardButton("🎵 YT Downloader", callback_data='yt_help')],
        [InlineKeyboardButton("📁 File to Link", callback_data='file_help')]
    ]
    await update.message.reply_photo(photo=PHOTO_URL, caption="𝑴𝒐𝒔𝒕 𝑷𝒐𝒘𝒆𝒓𝒇𝒖𝒍 𝑩𝒐𝒕 𝑾𝒊𝒕𝒉 निम्नलिखित 𝑭𝒆𝒂𝒕𝒖𝒓𝒆𝒔. \n\n𝑶𝒘𝒏𝒆𝒓 - 𝑼𝒎𝒆𝒔𝒉 𝑺𝒊𝒏𝒈𝒉 𝑮𝒖𝒓𝒋𝒂𝒓", reply_markup=InlineKeyboardMarkup(keyboard))

# --- 3. FLAT BUTTON HANDLER ---
async def handle_button(update, context):
    query = update.callback_query
    await query.answer()

    # Force Join Check
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, update.effective_user.id)
        if member.status in ['left', 'kicked']: return await query.edit_message_text(f"⚠️ Channel join karo: {CHANNEL_ID}")
    except: pass

    # Features
    if query.data == 'err':
        await query.edit_message_text("🔍 Searching... please wait...")
        await asyncio.sleep(3)
        await query.edit_message_text("❌ 𝑺𝒆𝒓𝒗𝒆𝒓 𝑲𝒊 𝑴𝒂 𝑪𝒉𝒖𝒅𝒊 𝑷𝒂𝒅𝒊 𝑯 𝑩𝒉𝒂𝒊 𝑬𝒏𝒈𝒍𝒊𝒔𝒉 𝑴𝒆 𝑩𝒐𝒍𝒆 𝑻𝒐 𝑺𝒆𝒓𝒗𝒆𝒓 𝑰𝒔𝒔𝒖𝒆𝒔.")
    elif query.data == 'tg_id':
        u = update.effective_user
        await query.edit_message_text(f"👤 Name: {u.first_name}\n🆔 ID: `{u.id}`\nUsername: @{u.username}")
    elif query.data == 'pin_help':
        await query.edit_message_text("Send: `/pin <pincode>`")
    elif query.data == 'ifsc_help':
        await query.edit_message_text("Send: `/ifsc <ifsc_code>`")
    elif query.data == 'yt_help':
        await query.edit_message_text("Send: `/yt <url>` to download.")
    elif query.data == 'file_help':
        await query.edit_message_text("Send me any file (PDF/IMG/ZIP), I will make a direct link for you.")

# --- 4. COMMANDS ---
# (ifsc_lookup, pin_lookup, download_yt, upload_file functions wahi purane wale yahan add karein)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.post_init = lambda a: a.bot.send_message(chat_id=LOG_CHANNEL_ID, text="🚀 Bot Online!")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    # Add your command handlers here
    app.run_polling()
                             
