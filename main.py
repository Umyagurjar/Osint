import asyncio
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ContextTypes
)

# --- CONFIGURATION ---
TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
ADMIN_ID = 6267863649 
LOG_CHANNEL_ID = -1004420089406 
REQUIRED_CHANNELS = ["@Gmoviesxb", "@Gmoviesxa"] 
PHOTO_URL = "https://graph.org/file/5ab741a9acc297d3df19e-48744a8755ad7e02b0.jpg"

# --- API FUNCTIONS ---
def get_ip_details(ip):
    try:
        data = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if data.get('status') == 'success':
            return f"🌐 **IP Details for {ip}:**\n📍 Country: {data['country']}\n🏙 City: {data['city']}\n🏢 ISP: {data['isp']}"
        return "❌ Invalid IP Address."
    except: return "⚠️ Error fetching IP."

def get_ifsc_details(ifsc):
    try:
        res = requests.get(f"https://ifsc.razorpay.com/{ifsc}", timeout=5)
        if res.status_code == 200:
            d = res.json()
            return f"🏦 **Bank Details:**\n🏢 Bank: {d['BANK']}\n📍 Branch: {d['BRANCH']}\n🏠 Address: {d['ADDRESS']}"
        return "❌ Invalid IFSC Code."
    except: return "⚠️ Error fetching IFSC."

# --- COMMAND HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    # Force Join Check
    for ch in REQUIRED_CHANNELS:
        try:
            m = await context.bot.get_chat_member(ch, user.id)
            if m.status in ['left', 'kicked']: raise Exception
        except:
            keyboard = [[InlineKeyboardButton(f"Join {ch}", url=f"https://t.me/{ch.replace('@', '')}")] for ch in REQUIRED_CHANNELS]
            keyboard.append([InlineKeyboardButton("✅ Check Joined", callback_data="check_join")])
            await update.message.reply_photo(PHOTO_URL, caption="❌ Bot use karne ke liye pehle in channels ko join karein:", reply_markup=InlineKeyboardMarkup(keyboard))
            return
    
    # Log User
    try: await context.bot.send_message(LOG_CHANNEL_ID, f"👤 User: {user.full_name} | ID: `{user.id}`")
    except: pass
    
    caption = "𝑴𝒐𝒔𝒕 𝑷𝒐𝒘𝒆𝒓𝒇𝒖𝒍 𝑩𝒐𝒕 𝑾𝒊𝒕𝒉 निम्नलिखित 𝑭𝒆𝒂𝒕𝒖𝒓𝒆𝒔. /n/n 𝑶𝒘𝒏𝒆𝒓 - 𝑼𝒎𝒆𝒔𝒉 𝑺𝒊𝒏𝒈𝒉 𝑮𝒖𝒓𝒋𝒂𝒓."
    k = [
        [InlineKeyboardButton("📱 Mobile", callback_data='mob'), InlineKeyboardButton("🆔 TG ID", callback_data='tg')],
        [InlineKeyboardButton("🌐 IP", callback_data='ip'), InlineKeyboardButton("🏦 IFSC", callback_data='ifsc')],
        [InlineKeyboardButton("📍 Pincode", callback_data='pin'), InlineKeyboardButton("🚗 Vehicle", callback_data='veh')]
    ]
    await update.message.reply_photo(PHOTO_URL, caption=caption, reply_markup=InlineKeyboardMarkup(k))

async def stats(update, context):
    if update.effective_user.id != ADMIN_ID: return
    unique = set()
    async for m in context.bot.get_chat_history(chat_id=LOG_CHANNEL_ID, limit=5000):
        if m.text and "ID: `" in m.text: unique.add(m.text.split("ID: `")[1].split("`")[0])
    await update.message.reply_text(f"📊 **Total Unique Users:** {len(unique)}")

async def broadcast(update, context):
    if update.effective_user.id != ADMIN_ID: return
    msg = " ".join(context.args)
    if not msg: return await update.message.reply_text("Usage: /broadcast <message>")
    unique = set()
    async for m in context.bot.get_chat_history(chat_id=LOG_CHANNEL_ID, limit=5000):
        if m.text and "ID: `" in m.text: unique.add(m.text.split("ID: `")[1].split("`")[0])
    
    count = 0
    for uid in unique:
        try: 
            await context.bot.send_message(int(uid), text=msg)
            count += 1
            await asyncio.sleep(0.05)
        except: continue
    await update.message.reply_text(f"✅ Broadcast Sent: {count} users.")

async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "check_join": await start(update, context)
    elif query.data == 'tg':
        u = query.from_user
        await query.message.reply_text(f"🆔 **Details:**\n👤 Name: {u.full_name}\n🆔 ID: `{u.id}`\n🔗 User: @{u.username}")
    elif query.data in ['ip', 'ifsc', 'mob', 'pin', 'veh']:
        context.user_data['waiting_for'] = query.data
        await query.message.reply_text(f"📥 Please apna {query.data.upper()} bhejein:")

async def handle_input(update, context):
    waiting = context.user_data.get('waiting_for')
    text = update.message.text
    if waiting == 'ip': await update.message.reply_text(get_ip_details(text), parse_mode="Markdown")
    elif waiting == 'ifsc': await update.message.reply_text(get_ifsc_details(text), parse_mode="Markdown")
    elif waiting in ['mob', 'pin', 'veh']:
        status_msg = await update.message.reply_text(f"🔍 Searching {waiting.upper()} for: {text}...")
        await asyncio.sleep(4)
        await status_msg.edit_text("⚠️ **Server Down!**\n\nDatabase busy hai. Please 5 minute baad try karein.")
    context.user_data['waiting_for'] = None

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app.run_polling()
    
