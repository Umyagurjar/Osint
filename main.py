import logging, requests, asyncio, yt_dlp, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
                          MessageHandler, filters, ConversationHandler)

TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
CHANNEL_ID = "@GMoviesXB"
LOG_CHANNEL = -1004420089406
PHOTO_URL = "https://graph.org/file/5ab741a9acc297d3df19e-48744a8755ad7e02b0.jpg"

INPUT_DATA = 1
started_users = set()

# --- FORCE JOIN ---
async def check_force_join(update, context):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['left', 'kicked']:
            await update.callback_query.message.reply_text(f"⚠️ **Channel join karo:** {CHANNEL_ID}")
            return False
        return True
    except: return False

# --- UI MENU ---
async def show_menu(update, edit=False):
    keyboard = [
        [InlineKeyboardButton("📱 Mobile Info", callback_data='req_m'), InlineKeyboardButton("🚗 Vehicle Info", callback_data='req_v')],
        [InlineKeyboardButton("📍 Pincode Lookup", callback_data='req_pin'), InlineKeyboardButton("🏦 IFSC Lookup", callback_data='req_ifsc')],
        [InlineKeyboardButton("🎵/🎥 YT Downloader", callback_data='req_yt'), InlineKeyboardButton("📁 File to Link", callback_data='req_file')],
        [InlineKeyboardButton("👤 TG Profile", callback_data='tg_profile')]
    ]
    if edit: await update.callback_query.edit_message_caption(caption="✨ **Mega Utility Hub**", reply_markup=InlineKeyboardMarkup(keyboard))
    else: await update.message.reply_photo(photo=PHOTO_URL, caption="✨ **Mega Utility Hub**", reply_markup=InlineKeyboardMarkup(keyboard))

async def start(update, context):
    if update.effective_user.id not in started_users:
        try: await context.bot.send_message(LOG_CHANNEL, f"👤 New User: {update.effective_user.first_name} (`{update.effective_user.id}`)")
        except: pass
        started_users.add(update.effective_user.id)
    await show_menu(update)
    return ConversationHandler.END

# --- HANDLERS ---
async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    if not await check_force_join(update, context): return
    
    if query.data == 'tg_profile':
        u = query.from_user
        await query.edit_message_caption(f"👤 {u.first_name}\n🆔 `{u.id}`\nUsername: @{u.username}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))
    elif query.data == 'req_yt':
        kb = [[InlineKeyboardButton("🎵 MP3", callback_data='dl_mp3'), InlineKeyboardButton("🎥 720p", callback_data='dl_720')], [InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        await query.edit_message_caption("Select Quality:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith('dl_'):
        context.user_data['format'] = query.data
        await query.edit_message_caption("🔗 Send YouTube Link:")
        return INPUT_DATA
    elif query.data.startswith('req_'):
        context.user_data['action'] = query.data
        await query.edit_message_caption("📝 Enter Details:")
        return INPUT_DATA

async def process_input(update, context):
    val = update.message.text
    action = context.user_data.get('action')
    fmt = context.user_data.get('format')
    
    if action == 'req_file' and update.message.document:
        file = await update.message.document.get_file()
        await file.download_to_drive("temp_file")
        with open("temp_file", 'rb') as f:
            res_json = requests.post("https://store1.gofile.io/uploadFile", files={'file': f}).json()
        await update.message.reply_text(f"🔗 Link: {res_json['data']['downloadPage']}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))
        os.remove("temp_file")
        return ConversationHandler.END

    await update.message.reply_text("⏳ Processing...")
    
    if action == 'req_pin':
        data = requests.get(f"https://api.postalpincode.in/pincode/{val}").json()
        res = f"📮 Area: {data[0]['PostOffice'][0]['Name']}\n📍 State: {data[0]['PostOffice'][0]['State']}" if data[0]['Status'] == 'Success' else "❌ Invalid."
    elif action == 'req_ifsc':
        data = requests.get(f"https://ifsc.razorpay.com/{val}").json()
        res = f"🏦 Bank: {data.get('BANK', 'Not Found')}" if 'BANK' in data else "❌ Invalid."
    elif fmt:
        try:
            ydl_opts = {'format': 'bestaudio' if fmt=='dl_mp3' else f'bestvideo[height<=720]+bestaudio/best', 'outtmpl': 'vid.mp4'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([val])
            await update.message.reply_document(open('vid.mp4', 'rb'))
            os.remove('vid.mp4'); return ConversationHandler.END
        except: res = "❌ Error."
    else:
        await asyncio.sleep(2)
        res = "❌ Server currently down."
        
    await update.message.reply_text(res, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start), CallbackQueryHandler(handle_callback)],
        states={INPUT_DATA: [MessageHandler(filters.TEXT | filters.Document.ALL, process_input)]},
        fallbacks=[CallbackQueryHandler(show_menu, pattern='back')]
    ))
    app.run_polling()
        
