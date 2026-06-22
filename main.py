import logging, httpx, os, threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("11461|WJlyTWDLdG0td5VikvvdPeNARIvJImF3W67N4q7D") 
BASE_API = "https://api.zylalabs.com/v1"

app = Flask(__name__)
@app.route('/')
def health(): return "Bot is running!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# --- API LOGIC ---
async def fetch_api_data(endpoint, user_input):
    # Har service ka specific path yahan define hai
    endpoints = {
        'num_info': '/reverse-phone-lookup/get-data',
        'ip_info': '/ip-lookup/info',
        'vehicle_full': '/vehicle-data/get',
        'pincode_info': '/pincode/details'
    }
    
    # Param mapping: Zyla Labs ke hisaab se (check documentation)
    params_map = {
        'num_info': 'number',
        'ip_info': 'ip',
        'vehicle_full': 'rc',
        'pincode_info': 'pincode'
    }

    url = BASE_API + endpoints.get(endpoint)
    param_name = params_map.get(endpoint)
    params = {param_name: user_input}
    headers = {"Authorization": f"Bearer {API_KEY}"}

    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, params=params, headers=headers, timeout=20.0)
            return r.json() if r.status_code == 200 else {"error": f"Status {r.status_code}", "msg": r.text}
        except Exception as e: return {"error": str(e)}

# --- BOT HANDLERS ---
async def start(update, context):
    k = [
        [InlineKeyboardButton("📱 Mobile", callback_data='num_info'), InlineKeyboardButton("🌐 IP", callback_data='ip_info')],
        [InlineKeyboardButton("🚗 Vehicle", callback_data='vehicle_full'), InlineKeyboardButton("📍 Pincode", callback_data='pincode_info')]
    ]
    await update.message.reply_text("Chuniye kya search karna hai:", reply_markup=InlineKeyboardMarkup(k))

async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    context.user_data['endpoint'] = query.data
    await query.message.reply_text(f"Selected: {query.data}. Ab data bhejein:")

async def handle_input(update, context):
    if 'endpoint' not in context.user_data:
        await update.message.reply_text("Pehle menu se kuch chunein.")
        return
    
    endpoint = context.user_data.pop('endpoint')
    await update.message.reply_text("🔍 Searching...")
    result = await fetch_api_data(endpoint, update.message.text)
    
    res_str = str(result)
    msg = "Result:\n```json\n" + res_str + "\n```"
    await update.message.reply_text(msg, parse_mode='Markdown')

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app_b = ApplicationBuilder().token(TOKEN).build()
    app_b.add_handler(CommandHandler("start", start))
    app_b.add_handler(CallbackQueryHandler(button_click))
    app_b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    app_b.run_polling()
    
