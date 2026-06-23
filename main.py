import logging, requests, os, asyncio, yt_dlp
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, filters, MessageHandler

TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
CHANNEL_ID = "@GMoviesXB"
LOG_CHANNEL_ID = -1004420089406
PHOTO_URL = "https://graph.org/file/5ab741a9acc297d3df19e-48744a8755ad7e02b0.jpg"

logging.basicConfig(level=logging.INFO)

# --- LOGGING ---
async def log_user(update, context):
    user = update.effective_user
    msg = f"👤 **New User:** {user.first_name} (@{user.username})\nID: `{user.id}`"
    await context.bot.send_message(chat_id=LOG_CHANNEL_ID, text=msg, parse_mode='Markdown')

# --- START MENU ---
async def start(update, context):
    await log_user(update, context)
    keyboard = [
        [InlineKeyboardButton("📱 Mobile/Vehicle/IP", callback_data='err')],
        [InlineKeyboardButton("👤 TG Profile", callback_data='tg_id'), InlineKeyboardButton("📍 Pincode/IFSC", callback_data='search_info')],
        [InlineKeyboardButton("🎵/🎥 YT Downloader", callback_data='yt_menu'), InlineKeyboardButton("📁 File to Link", callback_data='file_help')]
    ]
    await update.message.reply_photo(photo=PHOTO_URL, caption="𝑴𝒐𝒔𝒕 𝑷𝒐𝒘𝒆𝒓𝒇𝒖𝒍 𝑩𝒐𝒕 𝑾𝒊𝒕𝒉 निम्नलिखित 𝑭𝒆𝒂𝒕𝒖𝒓𝒆𝒔. /n𝑶𝒘𝒏𝒆𝒓 - 𝑼𝒎𝒆𝒔𝒉 𝑺𝒊𝒏𝒈𝒉 𝑮𝒖𝒓𝒋𝒂𝒓", reply_markup=InlineKeyboardMarkup(keyboard))

# --- BUTTON HANDLER ---
async def handle_button(update, context):
    query = update.callback_query
    await query.answer()
    
    # Force Join
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, update.effective_user.id)
        if member.status in ['left', 'kicked']: return await query.edit_message_text(f"⚠️ Join: {CHANNEL_ID}")
    except: pass

    if query.data == 'err':
        await query.edit_message_text("🔍 Searching...")
        await asyncio.sleep(3)
        await query.edit_message_text("❌ 𝑺𝒆𝒓𝒗𝒆𝒓 𝑲𝒊 𝑴𝒂 𝑪𝒉𝒖𝒅𝒊 𝑷𝒂𝒅𝒊 𝑯 𝑩𝒉𝒂𝒊 𝑬𝒏𝒈𝒍𝒊𝒔𝒉 𝑴𝒆 𝑩𝒐𝒍𝒆 𝑻𝒐 𝑺𝒆𝒓𝒗𝒆𝒓 𝑰𝒔𝒔𝒖𝒆𝒔.")
    elif query.data == 'tg_id':
        u = update.effective_user
        await query.edit_message_text(f"👤 Name: {u.first_name}\n🆔 ID: `{u.id}`\nUsername: @{u.username}")
    elif query.data == 'search_info':
        await query.edit_message_text("Use: /pin <code_or_pincode> OR /ifsc <code_or_ifsc>")
    elif query.data == 'file_help':
        await query.edit_message_text("Send me any file, and I will generate a direct download link!")
    elif query.data == 'yt_menu':
        keyboard = [
            [InlineKeyboardButton("🎵 MP3", callback_data='dl_mp3'), InlineKeyboardButton("🎥 144p", callback_data='dl_144')],
            [InlineKeyboardButton("🎥 360p", callback_data='dl_360'), InlineKeyboardButton("🎥 720p", callback_data='dl_720')]
        ]
        await query.edit_message_text("Select Quality:", reply_markup=InlineKeyboardMarkup(keyboard))
    elif query.data.startswith('dl_'):
        context.user_data['format'] = query.data
        await query.edit_message_text("✅ Format selected. Now send me the YouTube URL.")

# --- YT DOWNLOADER ---
async def handle_yt_url(update, context):
    if 'format' not in context.user_data: return await update.message.reply_text("First select format from menu!")
    url = update.message.text
    fmt_code = context.user_data['format']
    
    formats = {
        'dl_mp3': 'bestaudio/best',
        'dl_144': 'bestvideo[height<=144]+bestaudio/best',
        'dl_360': 'bestvideo[height<=360]+bestaudio/best',
        'dl_720': 'bestvideo[height<=720]+bestaudio/best'
    }
    
    await update.message.reply_text("⏳ Downloading...")
    try:
        ydl_opts = {'format': formats[fmt_code], 'outtmpl': 'down.%(ext)s', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}] if fmt_code == 'dl_mp3' else []}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url])
        await update.message.reply_document(document=open("down.mp3" if fmt_code=='dl_mp3' else "down.mp4", "rb"))
        os.remove("down.mp3" if fmt_code=='dl_mp3' else "down.mp4")
    except: await update.message.reply_text("❌ Download Failed.")

# --- FILE TO LINK ---
async def upload_file(update, context):
    file = await update.message.document.get_file()
    await file.download_to_drive("temp_file")
    with open("temp_file", 'rb') as f:
        res = requests.post("https://store1.gofile.io/uploadFile", files={'file': f}).json()
    await update.message.reply_text(f"🔗 Link: {res['data']['downloadPage']}")
    os.remove("temp_file")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.post_init = lambda a: a.bot.send_message(chat_id=LOG_CHANNEL_ID, text="🚀 Bot Online!")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_button))
    app.add_handler(MessageHandler(filters.Document.ALL, upload_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_yt_url))
    app.run_polling()
        
