import asyncio, threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8860791223:AAFIdnJb_YdwgI1fNNsGGTai24IAbyUD6eQ"
# Apni photo ka link yahan daalein
HEADER_PHOTO_URL = "https://graph.org/file/5ab741a9acc297d3df19e-48744a8755ad7e02b0.jpg" 

app = Flask(__name__)
@app.route('/')
def health(): return "Bot is running!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# --- HANDLERS ---
async def start(update, context):
    # Photo aur buttons bhejne ka code
    k = [
        [InlineKeyboardButton("📱 Mobile", callback_data='mob'), InlineKeyboardButton("🆔 TG ID", callback_data='tg')],
        [InlineKeyboardButton("🌐 IP", callback_data='ip'), InlineKeyboardButton("🏦 IFSC", callback_data='ifsc')],
        [InlineKeyboardButton("📍 Pincode", callback_data='pin'), InlineKeyboardButton("🚗 Vehicle", callback_data='veh')]
    ]
    
    await update.message.reply_photo(
        photo=HEADER_PHOTO_URL,
        caption="𝑴𝒐𝒔𝒕 𝑷𝒐𝒘𝒆𝒓𝒇𝒖𝒍 𝑩𝒐𝒕 𝑾𝒊𝒕𝒉 निम्नलिखित 𝑭𝒆𝒂𝒕𝒖𝒓𝒆

        
𝑶𝒘𝒏𝒆𝒓 - 𝑼𝒎𝒆𝒔𝒉 𝑺𝒊𝒏𝒈𝒉 𝑮𝒖𝒓𝒋𝒂𝒓.",
        reply_markup=InlineKeyboardMarkup(k)
    )

async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['selected'] = query.data
    await query.message.reply_text(f"Selected: {query.data}. Ab detail bhejein:")

async def handle_input(update, context):
    if 'selected' not in context.user_data:
        await update.message.reply_text("Pehle menu se button chunein.")
        return
    
    # User ko dikha rahe hain ki process ho raha hai
    status = await update.message.reply_text("🔍 Request process ho rahi hai...")
    
    # 3 second ka wait (Simulated processing)
    await asyncio.sleep(3)
    
    # Server Issue ka error message
    await status.edit_text("❌ Server Error: Server Ki Ma Chudi Padi H Dobara Try Karna Bhai😁😄")
    context.user_data.pop('selected')

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app_b = ApplicationBuilder().token(TOKEN).build()
    app_b.add_handler(CommandHandler("start", start))
    app_b.add_handler(CallbackQueryHandler(button_click))
    app_b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app_b.run_polling()
