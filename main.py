import logging, requests, os, yt_dlp
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
CHANNEL_ID = "@GMoviesXB"
LOG_CHANNEL = -1004420089406
PHOTO_URL = "https://graph.org/file/5ab741a9acc297d3df19e-48744a8755ad7e02b0.jpg"

# --- HELPERS ---
async def is_member(update, context):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status not in ['left', 'kicked']
    except: return False

async def show_menu(update, query=None):
    kb = [
        [InlineKeyboardButton("📱 Mobile/Vehicle", callback_data='err')],
        [InlineKeyboardButton("📍 Pincode", callback_data='pin_mode'), InlineKeyboardButton("🏦 IFSC", callback_data='ifsc_mode')],
        [InlineKeyboardButton("🎵 YT Downloader", callback_data='yt_mode'), InlineKeyboardButton("📁 File to Link", callback_data='file_mode')]
    ]
    if query: await query.edit_message_text("✨ **Menu:**", reply_markup=InlineKeyboardMarkup(kb))
    else: await update.message.reply_photo(photo=PHOTO_URL, caption="✨ **Main Menu:**", reply_markup=InlineKeyboardMarkup(kb))

# --- BUTTON HANDLER ---
async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if not await is_member(update, context): return await query.edit_message_text(f"⚠️ Join: {CHANNEL_ID}")
    
    data = query.data
    if data == 'back': await show_menu(update, query=query)
    elif data == 'err': await query.edit_message_text("❌ Server Down.", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))
    else:
        context.user_data['mode'] = data
        await query.edit_message_text(f"📝 {data.replace('_mode', '').upper()} selected. Enter details:", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))

# --- TEXT/FILE HANDLER ---
async def text_handler(update, context):
    mode = context.user_data.get('mode')
    if not mode: return
    
    val = update.message.text
    msg = await update.message.reply_text("⏳ Processing...")

    # LOGIC
    if mode == 'pin_mode':
        data = requests.get(f"https://api.postalpincode.in/pincode/{val}").json()
        res = f"📮 Area: {data[0]['PostOffice'][0]['Name']}\n📍 State: {data[0]['PostOffice'][0]['State']}" if data[0]['Status'] == 'Success' else "❌ Invalid."
    elif mode == 'ifsc_mode':
        data = requests.get(f"https://ifsc.razorpay.com/{val}").json()
        res = f"🏦 Bank: {data.get('BANK', 'Not Found')}" if 'BANK' in data else "❌ Invalid."
    elif mode == 'yt_mode':
        try:
            ydl_opts = {'format': 'best', 'outtmpl': 'vid.mp4'}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([val])
            await update.message.reply_document(document=open('vid.mp4', 'rb'))
            os.remove('vid.mp4')
            res = "✅ Download Complete!"
        except: res = "❌ Download Failed."
    else: res = "⚠️ Invalid action."

    await msg.edit_text(res, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back')]]))

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", show_menu))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    app.run_polling()
    
