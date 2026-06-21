import logging
import httpx
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, ContextTypes, CommandHandler, 
    CallbackQueryHandler, MessageHandler, filters
)

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
API_KEY = os.getenv("API_KEY", "Test")
CHANNEL_ID = "@YOUR_CHANNEL_USERNAME" # Yahan apne channel ka username daalein
BASE_DOMAIN = "https://sbsakib.eu.cc/apis"

# --- FLASK SERVER (Health Check) ---
app = Flask(__name__)
@app.route('/')
def health(): return "Bot is running!", 200

def run_flask(): app.run(host='0.0.0.0', port=8080)

# --- BOT LOGIC ---
logging.basicConfig(level=logging.INFO)

async def check_subscription(update, context):
    try:
        user_id = update.effective_user.id
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        if member.status in ['left', 'kicked']:
            keyboard = [[InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
            msg = "⚠️ Access Denied! Pehle hamara channel join karein."
            if update.callback_query: await update.callback_query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            else: await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return False
        return True
    except Exception as e:
        logging.error(f"Subscription Error: {e}")
        return True

async def fetch_api_data(endpoint, params):
    url = f"{BASE_DOMAIN}/{endpoint}"
    params['key'] = API_KEY
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(url, params=params, timeout=15.0)
            return r.json() if r.status_code == 200 else {"error": f"API Status: {r.status_code}"}
        except Exception as e: return {"error": str(e)}

async def handle_input(update, context):
    if not await check_subscription(update, context): return
    
    if 'endpoint' in context.user_data:
        endpoint = context.user_data.pop('endpoint')
        mapping = {'num_info': 'number', 'ip_info': 'ip', 'vehicle_full': 'rc', 'tg_username': 'user', 'pincode_info': 'pincode', 'ifsc_info': 'ifsc'}
        param_key = mapping.get(endpoint, 'query')
        
        await update.message.reply_text("🔍 Investigating, please wait...")
        result = await fetch_api_data(endpoint, {param_key: update.message.text})
        
        # FIX: JSON ko string mein convert karke alag se handle karein
        result_str = str(result)
        message_text = f"Result:\n```json\n{result_str}\n```"
        
        keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_menu')]]
        await update.message.reply_text(message_text, parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("❌ Pehle menu se option chunein.")
        
async def button_click(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == 'back_to_menu':
        await start(update, context)
    else:
        context.user_data['endpoint'] = query.data
        await query.message.reply_text(f"✅ {query.data.replace('_', ' ').upper()} selected. Ab input bhejein:")

async def handle_input(update, context):
    if not await check_subscription(update, context): return
    
    if 'endpoint' in context.user_data:
        endpoint = context.user_data.pop('endpoint')
        mapping = {'num_info': 'number', 'ip_info': 'ip', 'vehicle_full': 'rc', 'tg_username': 'user', 'pincode_info': 'pincode', 'ifsc_info': 'ifsc'}
        param_key = mapping.get(endpoint, 'query')
        
        await update.message.reply_text("🔍 Investigating, please wait...")
        result = await fetch_api_data(endpoint, {param_key: update.message.text})
        
        keyboard = [[InlineKeyboardButton("🔙 Main Menu", callback_data='back_to_menu')]]
        await update.message.reply_text(f"Result:\n```json\n{result}\n
```", parse_mode='Markdown', reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await update.message.reply_text("❌ Pehle menu se option chunein.")

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    bot_app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(CommandHandler("start", start))
    bot_app.add_handler(CallbackQueryHandler(button_click))
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_input))
    bot_app.run_polling()
                         
