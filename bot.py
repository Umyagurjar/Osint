import os
import logging
import socket
import requests
from dotenv import load_dotenv
from ipwhois import IPWhois
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

load_dotenv()
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not CHANNEL_USERNAME:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return True

async def send_join_request(update: Update) -> None:
    clean_username = CHANNEL_USERNAME.replace("@", "")
    invite_url = f"https://t.me{clean_username}"
    keyboard = [[InlineKeyboardButton("📢 Join Channel Here", url=invite_url)]]
    await update.message.reply_text(
        f"⚠️ *Access Denied!*\n\nJoin channel *{CHANNEL_USERNAME}* to use this OSINT bot.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return
    await update.message.reply_text(
        "🌐 *OSINT Bot Ready*\n\n"
        "📞 `/phone <number>` - Phone Leak Search\n"
        "🔍 `/domain <domain>` - WHOIS Lookup\n"
        "📍 `/ip <ip>` - IP Geolocation\n"
        "👤 `/user <username>` - Social Footprint",
        parse_mode="Markdown"
    )

async def phone_recon_leak(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/phone +91XXXXXXXXXX`", parse_mode="Markdown")
        return
    raw_phone = "".join(context.args)
    status_msg = await update.message.reply_text("⏳ Scanning registries...", parse_mode="Markdown")
    telephony_report = "📱 *Identity Profile:*\n"
    clean_num = raw_phone.replace("+", "").replace(" ", "").replace("-", "")
    try:
        parsed_num = phonenumbers.parse(raw_phone, None)
        if phonenumbers.is_valid_number(parsed_num):
            telephony_report += f"  • *Carrier:* {carrier.name_for_number(parsed_num, 'en')}\n  • *Country:* {geocoder.description_for_number(parsed_num, 'en')}\n"
    except Exception as e:
        telephony_report += f"  ⚠️ Metadata failed: {str(e)}\n"
    leak_report = "\n💥 *Breach Logs:*\n"
    try:
        res = requests.get(f"https://leakcheck.io{clean_num}", timeout=10)
        if res.status_code == 200 and res.json().get("success") and res.json().get("sources"):
            leak_report += f"🚨 *Compromised!* Total Leaks: `{res.json().get('total')}`\n"
            for source in res.json().get("sources", []):
                leak_report += f"  • `{source.get('name')}` ({source.get('date')})\n"
        else:
            leak_report += "✅ No active public data leak records found."
    except Exception as e:
        leak_report += f"❌ Request failed: {str(e)}"
    await status_msg.edit_text(telephony_report + leak_report, parse_mode="Markdown")

async def domain_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/domain example.com`")
        return
    clean_domain = context.args[0].replace("http://", "").replace("https://", "").split("/")[0]
    status_msg = await update.message.reply_text("⏳ Fetching domain info...")
    try:
        ip_addr = socket.gethostbyname(clean_domain)
        obj = IPWhois(ip_addr)
        results = obj.lookup_rdap(depth=1)
        response = f"🎯 *Domain:* {clean_domain}\n🖥️ *IP:* `{ip_addr}`\n🏢 *ISP:* {results.get('asn_description')}"
    except Exception as e:
        response = f"❌ Error: {str(e)}"
    await status_msg.edit_text(response, parse_mode="Markdown")

async def ip_geolocation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/ip 8.8.8.8`")
        return
    ip = context.args[0]
    status_msg = await update.message.reply_text("⏳ Tracking IP...")
    try:
        res = requests.get(f"http://ip-api.com{ip}", timeout=10).json()
        if res.get("status") == "success":
            response = f"📍 *IP:* {ip}\n🏳️ *Country:* {res.get('country')}\n🏙️ *City:* {res.get('city')}\n🌐 *ISP:* {res.get('isp')}"
        else:
            response = "❌ Invalid IP lookup."
    except Exception as e:
        response = f"❌ Timeout: {str(e)}"
    await status_msg.edit_text(response, parse_mode="Markdown")

async def user_recon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return
    if not context.args:
        await update.message.reply_text("❌ Usage: `/user username`")
        return
    username = context.args[0]
    status_msg = await update.message.reply_text("⏳ Hunting handles...")
    targets = {"GitHub": f"https://github.com{username}", "Reddit": f"https://reddit.com{username}"}
    found = []
    for platform, url in targets.items():
        try:
            res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
            found.append(f"✅ *{platform}:* [Link]({url})" if res.status_code == 200 else f"❌ *{platform}:* Not Found")
        except Exception:
            found.append(f"⚠️ *{platform}:* Timeout")
    await status_msg.edit_text(f"👤 *User:* {username}\n\n" + "\n".join(found), parse_mode="Markdown", disable_web_page_preview=True)

def main() -> None:
    if not TOKEN:
        print("CRITICAL: TELEGRAM_BOT_TOKEN is missing!")
        return
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("phone", phone_recon_leak))
    app.add_handler(CommandHandler("domain", domain_lookup))
    app.add_handler(CommandHandler("ip", ip_geolocation))
    app.add_handler(CommandHandler("user", user_recon))
    print("System polling loop started...")
    app.run_polling()

if __name__ == "__main__":
    main()
    
