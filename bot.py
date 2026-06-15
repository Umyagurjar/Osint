import os
import logging
import socket
import requests
from dotenv import load_dotenv
from ipwhois import IPWhois
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import TelegramError

# Advanced Telephony Engines
import phonenumbers
from phonenumbers import geocoder, carrier, timezone

# Setup environment variables and logs
load_dotenv()
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Fetch cloud engine infrastructure variables safely
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")

async def is_subscribed(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Validates if the user is a registered member of the tracking channel."""
    if not CHANNEL_USERNAME:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except TelegramError:
        return True

async def send_join_request(update: Update) -> None:
    """Forces non-subscribed users to join the target channel via an interactive button."""
    clean_username = CHANNEL_USERNAME.replace("@", "")
    invite_url = f"https://t.me{clean_username}"
    keyboard = [[InlineKeyboardButton("📢 Join Channel Here", url=invite_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"⚠️ *Access Denied!*\n\n"
        f"You must be a member of our channel *{CHANNEL_USERNAME}* to access the OSINT engine.\n"
        f"Please join the channel below and try your command again!",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends the operational dashboard commands menu."""
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return

    welcome_text = (
        "🌐 *Welcome to the Upgraded OSINT Bot* 🌐\n\n"
        "Deploy the following intelligence commands:\n"
        "📞 `/phone <number>` - Advanced Phone Recon & Leak Alert\n"
        "🔍 `/domain <domain>` - Fetch Domain IP & WHOIS profiles\n"
        "📍 `/ip <ip_address>` - Precise IP Geolocation tracking\n"
        "👤 `/user <username>` - Scan social footprint across networks\n\n"
        "_Ensure all query intelligence stays strictly compliant and ethical._"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def phone_recon_leak(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Extracts advanced phone analytics and executes global public data leak verification."""
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/phone +91XXXXXXXXXX` (Must include country code)", parse_mode="Markdown")
        return

    raw_phone = "".join(context.args)
    status_msg = await update.message.reply_text(f"⏳ Querying advanced registries for `{raw_phone}`...", parse_mode="Markdown")

    telephony_report = "📱 *Telephony & Identity Profile:*\n"
    clean_num_for_api = raw_phone.replace("+", "").replace(" ", "").replace("-", "")

    # Stage 1: Phone Formatting & Metadata Parsing
    try:
        parsed_num = phonenumbers.parse(raw_phone, None)
        if not phonenumbers.is_valid_number(parsed_num):
            await status_msg.edit_text("❌ Error: Target phone number is invalid or structurally incorrect.")
            return
        
        country_origin = geocoder.description_for_number(parsed_num, "en")
        service_provider = carrier.name_for_number(parsed_num, "en")
        timezones = timezone.time_zones_for_number(parsed_num)
        intl_format = phonenumbers.format_number(parsed_num, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
        
        telephony_report += (
            f"  • *Formatted Number:* `{intl_format}`\n"
            f"  • *Country Profile:* {country_origin}\n"
            f"  • *Carrier/Circle:* {service_provider if service_provider else 'Unknown / Virtual Number'}\n"
            f"  • *Zone Mapping:* {', '.join(timezones)}\n\n"
        )
    except Exception as e:
        telephony_report += f"  ⚠️ Formatting Extraction Failed: {str(e)}\n\n"

    # Stage 2: Public Privacy Breach Mapping Engine (Bypasses custom keys)
    leak_report = "💥 *Cyber Security Breach Logs (Public Data Sources):*\n"
    try:
        api_url = f"https://leakcheck.io{clean_num_for_api}"
        response = requests.get(api_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("sources"):
                leak_report += "🚨 *CRITICAL:* This number is compromised in public database breaches!\n"
                leak_report += f"📊 *Total Exposures Found:* `{data.get('total', 0)}`\n"
                leak_report += "🗂️ *Breached Environments List:* \n"
                
                for source in data.get("sources", []):
                    leak_report += f"  • `{source.get('name', 'N/A')}` ({source.get('date', 'N/A')})\n"
                
                leak_report += "\n💡 _Sec-Notice: Data leak mapped securely via public registries. True identities, plain passwords, and addresses are heavily restricted behind custom application credentials._"
            else:
                leak_report += "✅ No active public data breach records found for this phone number."
        else:
            leak_report += "⚠️ LeakCheck public endpoint limit hit or server busy. Try again later."
    except Exception as e:
        leak_report += f"❌ Failed to reach data breach lookup network: {str(e)}"

    final_report = f"🎯 *Target Intelligence Summary: {raw_phone}*\n\n" + telephony_report + leak_report
    await status_msg.edit_text(final_report, parse_mode="Markdown")

async def domain_lookup(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Resolves DNS names to check infrastructure ownership information."""
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/domain example.com`", parse_mode="Markdown")
        return

    raw_domain = "".join(context.args)
    clean_domain = raw_domain.replace("http://", "").replace("https://", "").split("/")[0]
    status_msg = await update.message.reply_text(f"⏳ Gathering domain info on `{clean_domain}`...", parse_mode="Markdown")
    
    try:
        ip_address = socket.gethostbyname(clean_domain)
        obj = IPWhois(ip_address)
        results = obj.lookup_rdap(depth=1)
        response = (
            f"🎯 *Domain OSINT Results: {clean_domain}*\n\n"
            f"🖥️ *IP Address:* `{ip_address}`\n"
            f"🏢 *ASN Provider:* {results.get('asn_description', 'Unknown')}\n"
            f"🌍 *Country Code:* {results.get('asn_country_code', 'Unknown')}\n"
        )
    except socket.gaierror:
        response = f"❌ Error: Could not resolve domain `{clean_domain}`."
    except Exception as e:
        response = f"❌ Error parsing domain profile: {str(e)}"
        
    await status_msg.edit_text(response, parse_mode="Markdown")

async def ip_geolocation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Traces structural geographical metrics matching an IP."""
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/ip 8.8.8.8`", parse_mode="Markdown")
        return

    ip = "".join(context.args)
    status_msg = await update.message.reply_text(f"⏳ Locating target IP `{ip}`...", parse_mode="Markdown")
    
    try:
        res = requests.get(f"http://ip-api.com{ip}", timeout=10).json()
        if res.get("status") == "success":
            response = (
                f"📍 *IP Geolocation Results: {ip}*\n\n"
                f"🏳️ *Country:* {res.get('country')}\n"
                f"🏙️ *City/Region:* {res.get('city')}, {res.get('regionName')}\n"
                f"🌐 *ISP:* {res.get('isp')}\n"
                f"🧭 *Coordinates:* `{res.get('lat')}, {res.get('lon')}`\n"
            )
        else:
            response = "❌ Target IP generated a routing validation failure."
    except Exception as e:
        response = f"❌ Connection timeout: {str(e)}"
        
    await status_msg.edit_text(response, parse_mode="Markdown")

async def user_recon(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Scans primary platforms for identical username handles."""
    if not await is_subscribed(update.effective_user.id, context):
        await send_join_request(update)
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: `/user username`", parse_mode="Markdown")
        return

    username = "".join(context.args)
    status_msg = await update.message.reply_text(f"⏳ Hunting networks for handle `{username}`...", parse_mode="Markdown")
    targets = {
        "GitHub": f"https://github.com{username}", 
        "Reddit": f"https://reddit.com{username}", 
        "Twitter/X": f"https://x.com{username}"
    }
    
    found_targets = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    for platform, url in targets.items():
        try:
            res = requests.get(url, headers=headers, timeout=5)
            found_targets.append(f"✅ *{platform}:* [Profile Link]({url})" if res.status_code == 200 else f"❌ *{platform}:* Not Found")
    
