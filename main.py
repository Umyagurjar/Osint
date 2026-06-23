import logging, requests, asyncio, yt_dlp, os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
                          MessageHandler, filters, ConversationHandler)

# CONFIG
TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
CHANNEL_ID = "@GMoviesXB"
LOG_CHANNEL = -1004420089406
PHOTO_URL = "https://graph.org/file/5ab741a9acc297d3df19e-48744a8755ad7e02b0.jpg"

INPUT_DATA = 1
started_users = set()

# --- UTILS ---
async def check_force_join(update, context):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['left', 'kicked']:
            await update.callback_query.message.reply_text(f"⚠️ Channel join karo: {CHANNEL_ID}")
            return False
        return True
    except: return True

async def show_menu(update, edit=False):
    keyboard = [
        [InlineKeyboardButton("📱 Mobile Info", callback_data='req_m'), InlineKeyboardButton("🚗 Vehicle Info", callback_data='req_v')],
        [InlineKeyboardButton("📍 Pincode Lookup", callback_data='req_pin'), InlineKeyboardButton("🏦 IFSC Lookup", callback_data='req_ifsc')],
        [InlineKeyboardButton("🎵/🎥 YT Downloader", callback_data='req_yt'), InlineKeyboardButton("📁 File to Link", callback_data='req_file')],
        [InlineKeyboardButton("👤 TG Profile", callback_data='tg_profile')]
    ]
    if edit:
        await update.callback_query.edit_message_caption(caption="✨ **Main Menu**", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_photo(photo=PHOTO_URL, caption="✨ **Main Menu**", reply_markup=InlineKeyboardMarkup(keyboard))

# --- ACTIONS ---
async def start(update, context):
    await show_menu(update)
    return ConversationHandler.END

async def back_to_menu(update, context):
    await show_menu(update, edit=True)
    return ConversationHandler.END

async def handle_callback(update, context):
    query = update.callback_query
    await query.answer()
    if not await check_force_join(update, context): return ConversationHandler.END
    
    if query.data == 'tg_profile':
        u = query.from_user
        await query.edit_message_caption(f"👤 Name: {u.first_name}\n🆔 `{u.id}`", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))
    elif query.data == 'req_yt':
        kb = [[InlineKeyboardButton("🎵 MP3", callback_data='dl_mp3'), InlineKeyboardButton("🎥 720p", callback_data='dl_720')], [InlineKeyboardButton("⬅️ Back", callback_data='back')]]
        await query.edit_message_caption("Select Format:", reply_markup=InlineKeyboardMarkup(kb))
    elif query.data.startswith('dl_'):
        context.user_data['format'] = query.data
        await query.edit_message_caption("🔗 Link bhejo:")
        return INPUT_DATA
    elif query.data == 'req_file':
        context.user_data['action'] = 'req_file'
        await query.edit_message_caption("📤 File bhejo:")
        return INPUT_DATA
    elif query.data.startswith('req_'):
        context.user_data['action'] = query.data
        await query.edit_message_caption("📝 Details bhejo:")
        return INPUT_DATA

async def process_input(update, context):
    action = context.user_data.get('action')
    fmt = context.user_data.get('format')
    val = update.message.text
    
    # File Handler
    if action == 'req_file' and update.message.document:
        file = await update.message.document.get_file()
        await file.download_to_drive("temp_file")
        with open("temp_file", 'rb') as f:
            res = requests.post("https://store1.gofile.io/uploadFile", files={'file': f}).json()
        await update.message.reply_text(f"🔗 {res['data']['downloadPage']}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))
        os.remove("temp_file")
    # API/YT Handler
    else:
        await update.message.reply_text("⏳ Processing...")
        # ... (Yahan logic likho)
        await update.message.reply_text("Done!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))
    return ConversationHandler.END

# --- MAIN ---
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start), CallbackQueryHandler(handle_callback)],
        states={INPUT_DATA: [MessageHandler(filters.TEXT | filters.Document.ALL, process_input)]},
        fallbacks=[CallbackQueryHandler(back_to_menu, pattern='back')]
    ))
    app.run_polling()
          
