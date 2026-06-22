import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- STATIC DATA (Yahan aap aur pincodes add kar sakte hain) ---
pincode_database = {
    "110001": "Delhi (Connaught Place)",
    "400001": "Mumbai (Fort)",
    "700001": "Kolkata (GPO)",
    "600001": "Chennai (George Town)",
    "560001": "Bengaluru (GPO)",
    "500001": "Hyderabad (GPO)",
    "380001": "Ahmedabad (GPO)",
    "411001": "Pune (GPO)",
    "302001": "Jaipur (GPO)",
    "226001": "Lucknow (GPO)"
}

TOKEN = "8150517089:AAGgRxsAOg6-nGZkIqo4MVJuXhchXc4XFl8" # Apna Token yahan daalein

app = Flask(__name__)
@app.route('/')
def health(): return "Bot is running!", 200
def run_flask(): app.run(host='0.0.0.0', port=8080)

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Pincode bhejein (e.g., 110001) main aapko city bata dunga.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    
    # Database mein search karein
    city_name = pincode_database.get(user_input)
    
    if city_name:
        await update.message.reply_text(f"📍 Pincode: {user_input}\n🏢 City: {city_name}")
    else:
        await update.message.reply_text("❌ Sorry, ye pincode hamare database mein nahi hai.")

if __name__ == '__main__':
    # Web server start
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Bot start
    app_b = ApplicationBuilder().token(TOKEN).build()
    app_b.add_handler(CommandHandler("start", start))
    app_b.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app_b.run_polling()
