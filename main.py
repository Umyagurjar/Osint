import logging, httpx, os, threading
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("API_KEY") # Ensure this is set in Render
BASE_API = "https://api.zylalabs.com/v1"

app = Flask(__name__)
@app.route('/')
def health(): return "Bot is running!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# --- API LOGIC ---
async def fetch_api_data(endpoint, user_input):
    # Zyla Labs Endpoints
    endpoints = {
        'num_info': '/reverse-phone-lookup/get-data',
        'ip_info': '/ip-lookup/info',
        'vehicle_full': '/vehicle-data/get',
        'pincode_info': '/pincode/details'
    }
    
    params_map = {
        'num_info': 'number',
        'ip_info': 'ip',
        'vehicle_full': 'rc',
        'pincode_info': 'pincode'
    }

    url = BASE_API + endpoints.get(endpoint)
    params = {params_map.get(endpoint): user_input}
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        try:
            # Timeout bada diya hai taaki slow response par bot na ruke
            r = await client.get(url, params=params, headers=headers, timeout=30.0)
            return r.json() if r.status_code == 200 else {"error": f"API Status {r.status_code}", "response": r.text}
        except Exception as e:
            return {"error": "Connection Failed", "details": str(e)}

# --- HANDLERS ---
async def start(update, context):
    k = [
        [InlineKeyboardButton("📱 Mobile", callback_data='num_info'), InlineKeyboardButton("🌐 IP", callback_data='ip_info')],
        [InlineKeyboardButton("🚗 Vehicle", callback_data='vehicle_full'), InlineKeyboardButton("📍 Pincode", callback_data='pincode_info')]
    ]
    await update.message.reply_text("Menu:", reply_markup=InlineKeyboardMarkup(k))

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
    msg = await update.message.reply_text("🔍 Searching...")
    
    result = await fetch_api_data(endpoint, update.message.text)
    
    # Message formatting
    res_str = str(result)
    final_text = f"Result:\n
http://googleusercontent.com/immersive_entry_chip/0
